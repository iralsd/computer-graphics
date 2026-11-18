
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from scipy.ndimage import label, binary_dilation
from scipy.optimize import fsolve
 

P, Q, TAU = 3.0, 9.0, 11.0
LIM = 4.0 
SIGMA_MAX = 20.0   
 
 
def ab(sigma, mu, a3):
    den = np.sin(sigma * (Q - P))
    c = 1.0 + a3 * np.cos(sigma * TAU)
    s = mu * sigma - a3 * np.sin(sigma * TAU)
    a1 = (-c * np.sin(sigma * Q) - s * np.cos(sigma * Q)) / den
    a2 = (c * np.sin(sigma * P) + s * np.cos(sigma * P)) / den
    return a1, a2, den
 
 
def branches(mu, a3, smax=SIGMA_MAX, lim=3 * LIM, step=2e-3):
    s = np.arange(1e-6, smax, step)
    a1, a2, den = ab(s, mu, a3)
    bad = (np.abs(a1) > lim) | (np.abs(a2) > lim) | ~np.isfinite(a1) | ~np.isfinite(a2)
    pole = np.zeros_like(bad)
    pole[1:] = np.sign(den[1:]) != np.sign(den[:-1])
    idx = np.flatnonzero(bad | pole)
    bounds = np.concatenate(([0], idx, [len(s)]))
    out = []
    for i in range(len(bounds) - 1):
        lo, hi = bounds[i], bounds[i + 1]
        if lo in idx:
            lo += 1
        if hi - lo > 1:
            out.append((a1[lo:hi], a2[lo:hi], s[lo:hi]))
    return out
 
 
def joined(br, clip=LIM):
    xs, ys = [], []
    for x, y, _ in br:
        x = np.where(np.abs(x) <= clip, x, np.nan)
        y = np.where(np.abs(y) <= clip, y, np.nan)
        xs += [x, [np.nan]]
        ys += [y, [np.nan]]
    return np.concatenate(xs), np.concatenate(ys)
 
 
def d0_region(br, a3, n=601):
    grid = np.zeros((n, n), bool)
 
    def put(x, y):
        ix = np.round((x + LIM) / (2 * LIM) * (n - 1)).astype(int)
        iy = np.round((y + LIM) / (2 * LIM) * (n - 1)).astype(int)
        ok = (ix >= 0) & (ix < n) & (iy >= 0) & (iy < n)
        grid[iy[ok], ix[ok]] = True
 
    cell = 2 * LIM / n
    for x, y, _ in br:
        d = np.hypot(np.diff(x), np.diff(y))
        k = np.maximum(1, np.ceil(d / cell)).astype(int)
        k = np.minimum(k, 400)
        t = np.concatenate([np.linspace(0, 1, kk, endpoint=False) for kk in k])
        rep = np.repeat(np.arange(len(k)), k)
        put(x[:-1][rep] + (x[1:] - x[:-1])[rep] * t, y[:-1][rep] + (y[1:] - y[:-1])[rep] * t)
    xs = np.linspace(-LIM, LIM, 4 * n)
    put(xs, -1 - a3 - xs)
    grid = binary_dilation(grid, iterations=1)
    lab, _ = label(~grid)
    c = lab[n // 2, n // 2]
    if c == 0:
        return None
    return lab == c
 
 
def find_nodes(br, mask, mu, a3):
    n = mask.shape[0]
    near = binary_dilation(mask, iterations=3)
 
    def inside(x, y):
        ix = np.round((x + LIM) / (2 * LIM) * (n - 1)).astype(int)
        iy = np.round((y + LIM) / (2 * LIM) * (n - 1)).astype(int)
        ok = (ix >= 0) & (ix < n) & (iy >= 0) & (iy < n)
        res = np.zeros(x.shape, bool)
        res[ok] = near[iy[ok], ix[ok]]
        return res
 
    X0, Y0, X1, Y1, S0, S1, B, I = [], [], [], [], [], [], [], []
    gid = 0
    for b, (x, y, s) in enumerate(br):
        keep = inside((x[:-1] + x[1:]) / 2, (y[:-1] + y[1:]) / 2)
        ii = np.flatnonzero(keep)
        X0.append(x[ii]); Y0.append(y[ii]); X1.append(x[ii + 1]); Y1.append(y[ii + 1])
        S0.append(s[ii]); S1.append(s[ii + 1]); B.append(np.full(len(ii), b)); I.append(ii + gid)
        gid += len(x)
    if not X0:
        return []
    X0, Y0, X1, Y1, S0, S1, B, I = [np.concatenate(v) for v in (X0, Y0, X1, Y1, S0, S1, B, I)]
    m = len(X0)
    if m < 2 or m > 6000:
        return []
    rx, ry = (X1 - X0)[:, None], (Y1 - Y0)[:, None]
    sx, sy = (X1 - X0)[None, :], (Y1 - Y0)[None, :]
    qx, qy = X0[None, :] - X0[:, None], Y0[None, :] - Y0[:, None]
    den = rx * sy - ry * sx
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (qx * sy - qy * sx) / den
        u = (qx * ry - qy * rx) / den
    far = (B[:, None] != B[None, :]) | (np.abs(I[:, None] - I[None, :]) > 3)
    hit = (np.abs(den) > 1e-14) & (t >= 0) & (t <= 1) & (u >= 0) & (u <= 1) & far
    hit = np.triu(hit, 1)
    ii, jj = np.nonzero(hit)
    nodes = []
    for i, j in zip(ii, jj):
        px = X0[i] + t[i, j] * (X1[i] - X0[i])
        py = Y0[i] + t[i, j] * (Y1[i] - Y0[i])
        if abs(px) > LIM or abs(py) > LIM:
            continue
        s1 = S0[i] + t[i, j] * (S1[i] - S0[i])
        s2 = S0[j] + u[i, j] * (S1[j] - S0[j])
 
        def f(v):
            xa, ya, _ = ab(np.array([v[0]]), mu, a3)
            xb, yb, _ = ab(np.array([v[1]]), mu, a3)
            return [xa[0] - xb[0], ya[0] - yb[0]]
        sol, info, ier, _ = fsolve(f, [s1, s2], full_output=True)
        if ier == 1 and np.max(np.abs(f(sol))) < 1e-8 and abs(sol[0] - sol[1]) > 1e-3 \
                and abs(sol[0] - s1) < 0.05 and abs(sol[1] - s2) < 0.05:
            s1, s2 = sol
        xa, ya, _ = ab(np.array([s1]), mu, a3)
        a, b_ = float(xa[0]), float(ya[0])
        if any(abs(a - na) < 2e-2 and abs(b_ - nb) < 2e-2 for na, nb, _, _ in nodes):
            continue
        nodes.append((a, b_, min(s1, s2), max(s1, s2)))
    nodes.sort(key=lambda z: (z[2], z[3]))
    return nodes
 
 
def find_line_nodes(br, mask, mu, a3):
    n = mask.shape[0]
    near = binary_dilation(mask, iterations=3)
    res = []
    for x, y, sg in br:
        g = 1 + x + y + a3
        k = np.flatnonzero(np.sign(g[:-1]) * np.sign(g[1:]) < 0)
        for i in k:
            t = g[i] / (g[i] - g[i + 1])
            s0 = sg[i] + t * (sg[i + 1] - sg[i])
            def f(v):
                a, b, _ = ab(np.array([v[0]]), mu, a3)
                return [1 + a[0] + b[0] + a3]
            sol, info, ier, _ = fsolve(f, [s0], full_output=True)
            if ier == 1 and abs(sol[0] - s0) < 0.05:
                s0 = float(sol[0])
            a, b, _ = ab(np.array([s0]), mu, a3)
            a, b = float(a[0]), float(b[0])
            if abs(a) > LIM or abs(b) > LIM:
                continue
            ix = int(round((a + LIM) / (2 * LIM) * (n - 1)))
            iy = int(round((b + LIM) / (2 * LIM) * (n - 1)))
            if 0 <= ix < n and 0 <= iy < n and near[iy, ix]:
                if not any(abs(a - r[0]) < 2e-2 and abs(b - r[1]) < 2e-2 for r in res):
                    res.append((a, b, s0))
    res.sort(key=lambda r: r[2])
    return res
 
 
fig = plt.figure(figsize=(15, 7.5))
ax3 = fig.add_axes([0.03, 0.30, 0.45, 0.65], projection='3d')
ax2 = fig.add_axes([0.55, 0.30, 0.40, 0.62])
s_a3 = Slider(fig.add_axes([0.10, 0.20, 0.30, 0.025]), 'a3', -0.99, 0.99, valinit=0.3, valstep=0.01)
s_mu = Slider(fig.add_axes([0.10, 0.09, 0.30, 0.025]), 'μ', 0.0, 1.0, valinit=0.5, valstep=0.01)
b_a3m = Button(fig.add_axes([0.10, 0.15, 0.06, 0.03]), '-')
b_a3p = Button(fig.add_axes([0.34, 0.15, 0.06, 0.03]), '+')
b_mum = Button(fig.add_axes([0.10, 0.04, 0.06, 0.03]), '-')
b_mup = Button(fig.add_axes([0.34, 0.04, 0.06, 0.03]), '+')
info = fig.text(0.50, 0.01, '', fontsize=8.5, va='bottom', family='monospace',
                bbox=dict(boxstyle='square', fc='white'))
FAMILY = np.linspace(-0.9, 0.9, 7)
ax3.view_init(elev=28, azim=-62) 
 
 
def update(_=None):
    mu, a3 = s_mu.val, s_a3.val
    br = branches(mu, a3)
    mask = d0_region(br, a3)
    nodes = find_nodes(br, mask, mu, a3) if mask is not None else []
    lnodes = find_line_nodes(br, mask, mu, a3) if mask is not None else []
 
    elev, azim = ax3.elev, ax3.azim 
    ax3.clear()
    ax3.view_init(elev=elev, azim=azim)
    sig = np.arange(0.1, 6.0, 0.1)
    A3 = np.linspace(-0.99, 0.99, 25)
    SX, SY, _ = ab(sig[:, None], mu, A3[None, :])
    bad = (np.abs(SX) > LIM) | (np.abs(SY) > LIM)
    SX = np.where(bad, np.nan, SX); SY = np.where(bad, np.nan, SY)
    SZ = np.broadcast_to(A3[None, :], SX.shape)
    pad = np.full((len(sig), 1), np.nan)
    ax3.plot(np.hstack([SX, pad]).ravel(), np.hstack([SY, pad]).ravel(),
             np.hstack([SZ, pad]).ravel(), color='#b4c4ea', lw=0.35)
    for a in FAMILY:
        x, y = joined(branches(mu, a, step=5e-3))
        ax3.plot(x, y, np.full_like(x, a), color='#b5c7ee', lw=0.6)
    x, y = joined(br)
    ax3.plot(x, y, np.full_like(x, a3), color='#0033cc', lw=2.0)
    g = np.linspace(-LIM, LIM, 17)
    G1, G2 = np.meshgrid(g, g)
    Z = -1 - G1 - G2
    Z[np.abs(Z) > 1.1] = np.nan
    ax3.plot_surface(G1, G2, Z, color='gray', alpha=0.25, linewidth=0)
    if nodes:
        ax3.scatter([n[0] for n in nodes], [n[1] for n in nodes], [a3] * len(nodes),
                    color='darkorange', edgecolor='k', s=40, depthshade=False)
    if lnodes:
        ax3.scatter([r[0] for r in lnodes], [r[1] for r in lnodes], [a3] * len(lnodes),
                    color='limegreen', marker='s', edgecolor='k', s=40, depthshade=False)
    ax3.set_xlim(-LIM, LIM); ax3.set_ylim(-LIM, LIM); ax3.set_zlim(-1.1, 1.1)
    ax3.set_box_aspect((1, 1, 0.75))
    ax3.set_xlabel('$a_1$'); ax3.set_ylabel('$a_2$'); ax3.set_zlabel('$a_3$')
    ax3.set_title('3D D-разбиение (серая плоскость: $1+a_1+a_2+a_3=0$)')
 
    ax2.clear()
    if mask is not None:
        ax2.imshow(np.where(mask, 1.0, np.nan), extent=(-LIM, LIM, -LIM, LIM), origin='lower',
                   cmap='Greens', vmin=0, vmax=2, alpha=.4, zorder=0)
    x, y = joined(br)
    ax2.plot(x, y, color='#2a6fb0', lw=1.3, label='D-разбиение')
    xs = np.array([-LIM, LIM])
    ax2.plot(xs, -1 - a3 - xs, 'r--', lw=1.5, label='$\\Sigma=0$: $1+a_1+a_2+a_3=0$')
    if nodes:
        ax2.scatter([n[0] for n in nodes], [n[1] for n in nodes], color='darkorange',
                    edgecolor='k', s=50, zorder=5, label='Узлы $D_0$')
        for k, nd in enumerate(nodes):
            ax2.annotate(f'P{k+1}', (nd[0], nd[1]), xytext=(4, 4), textcoords='offset points',
                         color='darkred', fontsize=9, weight='bold')
    if lnodes:
        ax2.scatter([r[0] for r in lnodes], [r[1] for r in lnodes], color='limegreen', marker='s',
                    edgecolor='k', s=50, zorder=5, label='Кривая ∩ $\\Sigma=0$')
        for k, r in enumerate(lnodes):
            ax2.annotate(f'Q{k+1}', (r[0], r[1]), xytext=(4, -12), textcoords='offset points',
                         color='darkgreen', fontsize=9, weight='bold')
    ax2.plot(0, 0, 'k+', ms=10)
    ax2.axhline(0, color='k', lw=.5); ax2.axvline(0, color='k', lw=.5)
    ax2.set_xlim(-LIM, LIM); ax2.set_ylim(-LIM, LIM); ax2.set_aspect('equal')
    ax2.grid(True, ls='--', alpha=.4)
    ax2.set_xlabel('$a_1$'); ax2.set_ylabel('$a_2$')
    ax2.set_title(f'2D срез: $a_1$ vs $a_2$ при $a_3={a3:.2f}$, $\\mu={mu:.2f}$')
    ax2.legend(loc='upper right', fontsize=8)
 
    lines = [f'Узлы D0 (самопересечения): {len(nodes)}']
    for k, (a, b, s1, s2) in enumerate(nodes[:5]):
        lines.append(f'P{k+1}: a1={a:.2f}, a2={b:.2f} | σ1={s1:.3f}, σ2={s2:.3f}, σ2/σ1={s2/s1:.3f}')
    lines.append(f'Пересечения с Σ=0 на границе D0: {len(lnodes)}')
    for k, (a, b, s1) in enumerate(lnodes[:4]):
        lines.append(f'Q{k+1}: a1={a:.2f}, a2={b:.2f} | σ={s1:.3f}')
    info.set_text('\n'.join(lines))
    print('\n'.join(lines)); print('---')
    fig.canvas.draw_idle()
 
 
def bump(slider, d):
    slider.set_val(float(np.clip(slider.val + d, slider.valmin, slider.valmax)))
 
 
s_a3.on_changed(update); s_mu.on_changed(update)
b_a3m.on_clicked(lambda e: bump(s_a3, -0.05)); b_a3p.on_clicked(lambda e: bump(s_a3, 0.05))
b_mum.on_clicked(lambda e: bump(s_mu, -0.05)); b_mup.on_clicked(lambda e: bump(s_mu, 0.05))
update()
 
if __name__ == '__main__':
    plt.show()

