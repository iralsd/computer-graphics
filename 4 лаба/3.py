import matplotlib.pyplot as plt
import numpy as np
import os

EPS = 1e-5  # нормальная точность

def get_code(x, y, xmin, ymin, xmax, ymax):
    code = 0
    if x < xmin: code |= 1
    if x > xmax: code |= 2
    if y < ymin: code |= 4
    if y > ymax: code |= 8
    return code

def midpoint(x1, y1, x2, y2, xmin, ymin, xmax, ymax, depth=0, max_depth=30):
    c1 = get_code(x1, y1, xmin, ymin, xmax, ymax)
    c2 = get_code(x2, y2, xmin, ymin, xmax, ymax)

    # Полностью внутри
    if c1 == 0 and c2 == 0:
        return [(x1, y1), (x2, y2)]

    # Полностью вне
    if (c1 & c2) != 0:
        return None

    # Ограничение рекурсии
    if depth > max_depth or (abs(x1 - x2) < EPS and abs(y1 - y2) < EPS):
        return [(x1, y1), (x2, y2)]

    # Делим пополам
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2

    left = midpoint(x1, y1, mx, my, xmin, ymin, xmax, ymax, depth + 1, max_depth)
    right = midpoint(mx, my, x2, y2, xmin, ymin, xmax, ymax, depth + 1, max_depth)

    # Склейка
    if left and right:
        return [left[0], right[1]]
    return left if left else right

# ---------- ВВОД ----------
input_file = "input_3.txt"

if not os.path.exists(input_file):
    with open(input_file, "w") as f:
        f.write("-4 -4 4 4 -2 -6 5 2")

with open(input_file, "r") as f:
    data = list(map(float, f.read().split()))
    xmin, ymin, xmax, ymax = data[0:4]
    x1, y1, x2, y2 = data[4:8]

res = midpoint(x1, y1, x2, y2, xmin, ymin, xmax, ymax)

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

# Окно
plt.plot(
    [xmin, xmax, xmax, xmin, xmin],
    [ymin, ymin, ymax, ymax, ymin],
    linewidth=2
)

# Исходный отрезок
plt.plot([x1, x2], [y1, y2], linestyle='--', alpha=0.4)

# Отсечённый
if res:
    rx, ry = zip(*res)
    plt.plot(rx, ry, linewidth=3)
    plt.scatter(rx, ry, zorder=5)

plt.gca().set_aspect('equal')
plt.xlim(-limit, limit)
plt.ylim(-limit, limit)

plt.title("Алгоритм средней точки")
plt.show()