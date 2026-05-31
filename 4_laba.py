import numpy as np
import matplotlib.pyplot as plt

H   = 0.02
EPS = 0.25

def f1(x, y): return 1 - x**2 - y**2
def f2(x, y): return 2*x*y

def rk3_step(x, y):
    Q1x = H * f1(x, y)
    Q1y = H * f2(x, y)
    Q2x = H * f1(x+Q1x/2, y+Q1y/2)
    Q2y = H * f2(x+Q1x/2, y+Q1y/2)
    Q3x = H * f1(x-Q1x+2*Q2x, y-Q1y+2*Q2y)
    Q3y = H * f2(x-Q1x+2*Q2x, y-Q1y+2*Q2y)
    return x + (Q1x + 4*Q2x + Q3x)/6, y + (Q1y + 4*Q2y + Q3y)/6

def integrate(x0, y0, T, max_r=20.0):
    xs, ys = [x0], [y0]
    x, y = x0, y0
    for i in range(int(T / H)):
        try:   x, y = rk3_step(x, y)
        except: break
        if not (np.isfinite(x) and np.isfinite(y)): break
        xs.append(x); ys.append(y)
        if abs(x) > max_r or abs(y) > max_r: break
    return np.array(xs), np.array(ys)

print("=" * 55)
print("  Вариант 10")
print("  Система дифференциальных уравнений:")
print("    dx/dt  =  1 - x^2 - y^2")
print("    dy/dt  =  2xy")
print("=" * 55)

print("""
─────────────────────────────────────────────────────
  ШАГ 1. Нахождение особых точек
─────────────────────────────────────────────────────
  Особые точки — решения системы f1=0, f2=0:

    f1 = 1 - x^2 - y^2 = 0   =>   x^2 + y^2 = 1
    f2 = 2xy = 0              =>   x=0  или  y=0

  При x=0:  1 - y^2 = 0  =>  y = ±1
  При y=0:  1 - x^2 = 0  =>  x = ±1

  Особые точки:
    P1 = (1,  0)
    P2 = (-1, 0)
    P3 = (0,  1)
    P4 = (0, -1)
""")

print("""─────────────────────────────────────────────────────
  ШАГ 2. Матрица Якоби
─────────────────────────────────────────────────────
  Линеаризация системы в окрестности точки (x0, y0):

        | df1/dx  df1/dy |   | -2x  -2y |
    A = |                | = |          |
        | df2/dx  df2/dy |   |  2y   2x |

  Характеристическое уравнение:
    λ^2 - tr(A)·λ + det(A) = 0
    tr(A)  = -2x + 2x = 0  (для всех точек)
    det(A) = (-2x)(2x) - (-2y)(2y) = -4x^2 + 4y^2 = 4(y^2 - x^2)
""")

singular = [(1,0,"P1=(1,0)"),(-1,0,"P2=(-1,0)"),(0,1,"P3=(0,1)"),(0,-1,"P4=(0,-1)")]

print("─────────────────────────────────────────────────────")
print("  ШАГ 3. Анализ каждой особой точки")
print("─────────────────────────────────────────────────────")

kinds = {}
for px, py, name in singular:
    A   = np.array([[-2*px,-2*py],[2*py,2*px]])
    lam = np.linalg.eigvals(A)
    tr  = round(np.trace(A), 8)
    det = round(np.linalg.det(A), 8)
    disc = tr**2 - 4*det

    print(f"\n  {name}:")
    print(f"    A = [[-{2*abs(px):.0f}, -{2*abs(py):.0f}], [{2*abs(py):.0f}, {2*px:.0f}]]  "
          f"=>  tr={tr:.1f},  det={det:.1f}")
    print(f"    D = tr^2 - 4·det = 0 - 4·({det:.1f}) = {disc:.1f}")

    if np.isclose(lam[0].imag, 0):# мнимая часть равна нулю
        l1, l2 = sorted(lam.real)
        print(f"    λ1 = {l1:.2f},  λ2 = {l2:.2f}  (вещественные)")
        if l1 * l2 < 0:
            kind = "СЕДЛО (неустойчиво)"
            print(f"    Вдоль оси x — устойч. сепаратриса")
            print(f"    Вдоль оси y — неустойч. сепаратриса")
        elif l1 < 0 and l2 < 0:
            kind = "УСТОЙЧИВЫЙ УЗЕЛ"
        else:
            kind = "НЕУСТОЙЧИВЫЙ УЗЕЛ"
        print(f"    => {kind}")
    else:
        re = 0.0 if abs(lam[0].real) < 1e-9 else lam[0].real
        im = abs(lam[0].imag)
        print(f"    D < 0, Re(λ) = {re:.2f}  =>  комплексные собственные значения")
        print(f"    λ = {re:.2f} ± {im:.2f}i")
        
        if np.isclose(re, 0):#вещественная часть равна нулю
            kind = "ЦЕНТР (линейн.)"
            print(f"    => {kind}")
            print(f"    Период орбиты T = 2π/ω = 2π/{im:.0f} ≈ {2*np.pi/im:.4f}")
        elif re < 0:
            kind = "УСТОЙЧИВЫЙ ФОКУС"
            print(f"    => {kind}")
        else:
            kind = "НЕУСТОЙЧИВЫЙ ФОКУС"
            print(f"    => {kind}")
    kinds[name] = kind
    
print(f"""
─────────────────────────────────────────────────────
  ШАГ 4. Метод и погрешность
─────────────────────────────────────────────────────
  Используется метод 3 — Рунге-Кутта 3-го порядка
  , h = {H}

  Формулы для системы :
    Q1x = h·f1(xk, yk),         Q1y = h·f2(xk, yk)
    Q2x = h·f1(xk+Q1x/2, yk+Q1y/2)
    Q2y = h·f2(xk+Q1x/2, yk+Q1y/2)
    Q3x = h·f1(xk - Q1x + 2Q2x,  yk - Q1y + 2Q2y)
    Q3y = h·f2(xk - Q1x + 2Q2x,  yk - Q1y + 2Q2y)

    x_{{k+1}} = xk + (Q1x + 4·Q2x + Q3x) / 6
    y_{{k+1}} = yk + (Q1y + 4·Q2y + Q3y) / 6

  Локальная погрешность:  O(h^4) = {H**4:.2e}
  Глобальная погрешность: O(h^3) = {H**3:.2e}
─────────────────────────────────────────────────────
""")



COLORS = ["#e41a1c", "#377eb8", "#4daf4a", "#ff7f00"]

T_cfg = {
    "P1=(1,0)":  10.0,
    "P2=(-1,0)": 10.0,
    "P3=(0,1)":  3.228,  
    "P4=(0,-1)": 3.228,
}
view = {
    "P1=(1,0)":  (-0.4, 2.4, -2.0, 2.0),
    "P2=(-1,0)": (-2.4, 0.4, -2.0, 2.0),
    "P3=(0,1)":  (-0.55, 0.55, 0.5, 1.55),
    "P4=(0,-1)": (-0.55, 0.55, -1.55, -0.5),
}

fig, axes = plt.subplots(2, 2, figsize=(13, 11))
fig.suptitle(
    "Вариант 10 — Фазовые портреты\n"
    r"$\dot{x} = 1-x^2-y^2$,   $\dot{y} = 2xy$"
    f"\nМетод РК-3,  h = {H},  ε = {EPS}",
    fontsize=13
)

for ax, (px, py, name) in zip(axes.flat, singular):
    T  = T_cfg[name]
    x1, x2, y1, y2 = view[name]
    ics = [(px+EPS, py), (px-EPS, py), (px, py+EPS), (px, py-EPS)]

    for (x0, y0), color in zip(ics, COLORS):
        xs, ys = integrate(x0, y0, T)
        ax.plot(xs, ys, color=color, linewidth=2.2)
        ax.plot(xs[0],  ys[0],  "o", color=color, markersize=10, zorder=5,
                markeredgecolor="white", markeredgewidth=1.5,
                label=f"({x0:.2f}, {y0:.2f})")
        ax.plot(xs[-1], ys[-1], "s", color=color, markersize=10, zorder=5,
                markeredgecolor="white", markeredgewidth=1.5)

    ax.plot(px, py, "k*", markersize=18, zorder=10)
    ax.set_xlim(x1, x2); ax.set_ylim(y1, y2)
    ax.set_title(f"{name}  —  {kinds[name]}", fontsize=10, pad=6)
    ax.set_xlabel("x", fontsize=11); ax.set_ylabel("y", fontsize=11)
    ax.legend(fontsize=8, title="○ старт   □ конец",
              framealpha=0.9, edgecolor="#aaaaaa", loc="best")
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_aspect("equal", "box")

plt.tight_layout()
plt.savefig("phase_portrait_var10.png", dpi=150, bbox_inches="tight")
plt.show()
