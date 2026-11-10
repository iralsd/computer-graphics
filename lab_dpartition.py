
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from scipy.ndimage import label, binary_dilation
 
P, Q = 3.0, 9.0
LIM = 5.0
 
 
def a1a2(sigma, mu, p=P, q=Q):
    den = np.sin(sigma * (q - p))
    a1 = -(np.sin(sigma * q) + mu * sigma * np.cos(sigma * q)) / den
    a2 = (np.sin(sigma * p) + mu * sigma * np.cos(sigma * p)) / den
    return a1, a2, den
 
 
def curve_branches(mu, s_min, s_max, lim, step=2e-4):
    s = np.arange(max(s_min, 1e-6), s_max, step)
    a1, a2, den = a1a2(s, mu)
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
 
 
def stable_region(branches, lim, n=700):
    grid = np.zeros((n, n), bool)
    xs = np.linspace(-lim, lim, n)
 
    def put(x, y):
        ix = np.round((x + lim) / (2 * lim) * (n - 1)).astype(int)
        iy = np.round((y + lim) / (2 * lim) * (n - 1)).astype(int)
        ok = (ix >= 0) & (ix < n) & (iy >= 0) & (iy < n)
        grid[iy[ok], ix[ok]] = True
 
    for x, y, _ in branches:
        k = int(max(1, np.max(np.hypot(np.diff(x), np.diff(y))) / (2 * lim / n)))
        t = np.linspace(0, 1, k + 1)[:-1]
        put((x[:-1, None] + (x[1:] - x[:-1])[:, None] * t).ravel(),
            (y[:-1, None] + (y[1:] - y[:-1])[:, None] * t).ravel())
    put(xs, -1 - xs)
    grid = binary_dilation(grid, iterations=1)
    lab, _ = label(~grid)
    c = lab[n // 2, n // 2]
    if c == 0:
        return None
    return (lab == c), (-lim, lim, -lim, lim)
 
 
def count_unstable_roots(a1, a2, mu, p=P, q=Q):
    R = (1 + abs(a1) + abs(a2)) / mu + 1.0
    N = int(min(2_000_000, max(50000, 200 * R * q)))
    th = np.linspace(-np.pi / 2, np.pi / 2, N)
    arc = R * np.exp(1j * th)                        # снизу вверх по дуге справа
    axis = 1j * np.linspace(R, -R, N)                # сверху вниз по мнимой оси
    lam = np.concatenate([arc, axis])                # контур против часовой стрелки
    val = mu * lam + 1 + a1 * np.exp(-lam * p) + a2 * np.exp(-lam * q)
    if np.min(np.abs(val)) < 1e-6:
        return None                                  # корень на границе
    total = np.sum(np.diff(np.unwrap(np.angle(val))))
    return int(round(total / (2 * np.pi)))
 
 
fig, ax = plt.subplots(figsize=(11, 8.5))
plt.subplots_adjust(bottom=0.30)
s_mu = Slider(plt.axes([0.15, 0.21, 0.55, 0.025]), 'μ', 0.01, 1.0, valinit=0.5, valstep=0.01)
s_smin = Slider(plt.axes([0.15, 0.17, 0.55, 0.025]), 'σ_min', 0.0, 60.0, valinit=0.0, valstep=0.01)
s_smax = Slider(plt.axes([0.15, 0.13, 0.55, 0.025]), 'σ_max', 1.0, 60.0, valinit=20.0, valstep=0.5)
s_pt = Slider(plt.axes([0.15, 0.09, 0.55, 0.025]), 'σ (точка)', 0.0, 60.0, valinit=1.0, valstep=0.01)
btn = Button(plt.axes([0.76, 0.12, 0.2, 0.08]), 'Проверить\nустойчивость', color='lightblue')
res_txt = fig.text(0.15, 0.03, '', fontsize=11)
 
state = {'branches': [], 'pt': None}
hover = ax.text(0.02, 0.98, '', transform=ax.transAxes, va='top',
                bbox=dict(boxstyle='round', fc='white', alpha=.85))
 
 
def mark(sig, mu, style, label_txt, off):
    x, y, _ = a1a2(np.array([sig]), mu)
    if sig > 1e-6 and np.isfinite(x[0]) and np.isfinite(y[0]):
        ax.plot(x, y, style, ms=8, mfc=style[0] if style[1] == 'o' else 'none', mew=2)
        ax.annotate(f'{label_txt}={sig:.2f}\n({x[0]:.3f}, {y[0]:.3f})', (x[0], y[0]),
                    xytext=off, textcoords='offset points', fontsize=9)
        return float(x[0]), float(y[0])
    print(f'{label_txt}={sig:.4f}: особая точка (разрыв)')
    return None
 
 
def update(_=None):
    global hover
    mu, smin, smax, sp = s_mu.val, s_smin.val, max(s_smax.val, s_smin.val + 0.5), s_pt.val
    ax.clear()
    br = curve_branches(mu, smin, smax, lim=LIM * 3)
    state['branches'] = br
 
    reg = stable_region(br, LIM) if smin == 0 else None
    if reg is not None:
        mask, ext = reg
        ax.imshow(np.where(mask, 1.0, np.nan), extent=ext, origin='lower',
                  cmap='Greens', vmin=0, vmax=2, alpha=.45, zorder=0)
    for x, y, _ in br:
        ax.plot(x, y, color='#1f77b4', lw=1.3)
    xs = np.array([-LIM, LIM])
    ax.plot(xs, -1 - xs, 'g--', lw=1.8, label='$a_1+a_2=-1$ (σ=0, λ=0)')
 
    state['pt'] = mark(sp, mu, 'ro', 'σ', (6, 6))
    mark(3 * sp, mu, 'bs', '3σ', (6, -22))
 
    ax.plot(0, 0, 'k+', ms=12)
    ax.axhline(0, color='k', lw=.5)
    ax.axvline(0, color='k', lw=.5)
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_aspect('equal')
    ax.grid(True, ls='--', alpha=.4)
    ax.set_xlabel('$a_1$')
    ax.set_ylabel('$a_2$')
    ax.set_title(f'D-разбиение: p={P:g}, q={Q:g}, a3=0, μ={mu:.2f}, σ∈[{smin:.1f}, {smax:.1f}]')
    ax.legend(loc='upper right')
    hover = ax.text(0.02, 0.98, '', transform=ax.transAxes, va='top',
                    bbox=dict(boxstyle='round', fc='white', alpha=.85))
    res_txt.set_text('')
    fig.canvas.draw_idle()
 
 
def sides_counts(sig, mu, eps=2e-3):
    h = 1e-5
    x1, y1, _ = a1a2(np.array([sig - h]), mu)
    x2, y2, _ = a1a2(np.array([sig + h]), mu)
    x0, y0, _ = a1a2(np.array([sig]), mu)
    t = np.array([x2[0] - x1[0], y2[0] - y1[0]])
    t /= np.linalg.norm(t)
    nrm = np.array([-t[1], t[0]])
    pa = np.array([x0[0], y0[0]]) + eps * nrm
    pb = np.array([x0[0], y0[0]]) - eps * nrm
    return (count_unstable_roots(pa[0], pa[1], mu), tuple(pa)), \
           (count_unstable_roots(pb[0], pb[1], mu), tuple(pb))
 
 
def check(_=None):
    if state['pt'] is None:
        res_txt.set_text('Сначала выберите точку σ (не в разрыве)')
    else:
        (na, pa), (nb, pb) = sides_counts(s_pt.val, s_mu.val)
        res_txt.set_text(f'Точка на кривой (граница). Корней с Re>0 по сторонам кривой: '
                         f'{na} и {nb} (при переходе пара корней пересекает мнимую ось)')
    fig.canvas.draw_idle()
 
 
def on_move(ev):
    if ev.inaxes is not ax or not state['branches']:
        return
    best = (np.inf, None)
    for x, y, s in state['branches']:
        d = (x - ev.xdata) ** 2 + (y - ev.ydata) ** 2
        i = int(np.argmin(d))
        if d[i] < best[0]:
            best = (d[i], (x[i], y[i], s[i]))
    if best[1] is not None:
        hover.set_text(f'a1={best[1][0]:.4f}, a2={best[1][1]:.4f}, σ={best[1][2]:.4f}')
        fig.canvas.draw_idle()
 
 
for s in (s_mu, s_smin, s_smax, s_pt):
    s.on_changed(update)
btn.on_clicked(check)
fig.canvas.mpl_connect('motion_notify_event', on_move)
update()
 
if __name__ == '__main__':
    plt.show()
 
