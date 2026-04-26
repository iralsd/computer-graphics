import matplotlib.pyplot as plt
import numpy as np
import os

def polygon_orientation(poly):
    s = 0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += (x2 - x1) * (y2 + y1)
    return s  # >0 — CW, <0 — CCW

def cyrus_beck(p0, p1, poly):
    x1, y1 = p0
    x2, y2 = p1
    dx, dy = x2 - x1, y2 - y1

    t_in = 0.0
    t_out = 1.0

    # Определяем ориентацию полигона
    orientation = polygon_orientation(poly)

    for i in range(len(poly)):
        p_curr = poly[i]
        p_next = poly[(i + 1) % len(poly)]

        # Вектор ребра
        ex = p_next[0] - p_curr[0]
        ey = p_next[1] - p_curr[1]

        # ВЫБОР ПРАВИЛЬНОЙ ВНЕШНЕЙ НОРМАЛИ
        if orientation < 0:  # CCW
            nx, ny = ey, -ex
        else:  # CW
            nx, ny = -ey, ex

        # Вектор от вершины к началу отрезка
        wx = x1 - p_curr[0]
        wy = y1 - p_curr[1]

        num = wx * nx + wy * ny
        den = dx * nx + dy * ny

        if den == 0:
            if num > 0:
                return None  # полностью вне
            else:
                continue  # параллельно и внутри
        t = -num / den

        if den < 0:
            t_in = max(t_in, t)
        else:
            t_out = min(t_out, t)

        if t_in > t_out:
            return None  # ранний выход

    return [
        (x1 + t_in * dx, y1 + t_in * dy),
        (x1 + t_out * dx, y1 + t_out * dy)
    ]

# ---------- ВВОД ----------
input_file = "input_1.txt"

if not os.path.exists(input_file):
    with open(input_file, "w") as f:
        f.write("0 5 -5 2 -3 -5 3 -5 5 2 -8 -1 8 4")

with open(input_file, "r") as f:
    data = list(map(float, f.read().split()))
    poly = [data[i:i+2] for i in range(0, 10, 2)]
    p0 = [data[10], data[11]]
    p1 = [data[12], data[13]]

res = cyrus_beck(p0, p1, poly)

# ---------- ОТРИСОВКА ----------
limit = 10
vals = np.arange(-limit, limit + 1, 1)

plt.figure(figsize=(8, 8))
plt.xticks(vals)
plt.yticks(vals)
plt.grid(True)
plt.minorticks_on()
plt.grid(which='minor', linestyle=':', linewidth=0.5)

plt.axhline(0, linewidth=1)
plt.axvline(0, linewidth=1)

# Полигон
poly_draw = poly + [poly[0]]
px, py = zip(*poly_draw)
plt.plot(px, py, linewidth=2)

# Исходный отрезок
plt.plot([p0[0], p1[0]], [p0[1], p1[1]], linestyle='--', alpha=0.4)

# Отсечённый
if res:
    rx, ry = zip(*res)
    plt.plot(rx, ry, linewidth=3)
    plt.scatter(rx, ry, zorder=5)

plt.gca().set_aspect('equal')
plt.xlim(-limit, limit)
plt.ylim(-limit, limit)

plt.title("Алгоритм Цируса–Бека (отсечение отрезка)")
plt.show()