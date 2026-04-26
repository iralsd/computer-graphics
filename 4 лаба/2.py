import matplotlib.pyplot as plt
import numpy as np
import os

def get_code(x, y, xmin, ymin, xmax, ymax):
    code = 0
    if x < xmin: code |= 1   # LEFT
    if x > xmax: code |= 2   # RIGHT
    if y < ymin: code |= 4   # BOTTOM
    if y > ymax: code |= 8   # TOP
    return code

def sutherland_cohen(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    while True:
        c1 = get_code(x1, y1, xmin, ymin, xmax, ymax)
        c2 = get_code(x2, y2, xmin, ymin, xmax, ymax)

        # Полностью внутри
        if c1 == 0 and c2 == 0:
            return [(x1, y1), (x2, y2)]

        # Полностью вне
        if (c1 & c2) != 0:
            return None

        # Выбираем внешнюю точку
        c = c1 if c1 != 0 else c2

        if c & 8:  # TOP
            if y2 == y1: return None
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax

        elif c & 4:  # BOTTOM
            if y2 == y1: return None
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin

        elif c & 2:  # RIGHT
            if x2 == x1: return None
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax

        elif c & 1:  # LEFT
            if x2 == x1: return None
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin

        # Обновляем нужную точку
        if c == c1:
            x1, y1 = x, y
        else:
            x2, y2 = x, y

# ---------- ВВОД ----------
input_file = "input_2.txt"

if not os.path.exists(input_file):
    with open(input_file, "w") as f:
        f.write("-4 -4 4 4 -7 -2 5 6")

with open(input_file, "r") as f:
    data = list(map(float, f.read().split()))
    xmin, ymin, xmax, ymax = data[0:4]
    x1, y1, x2, y2 = data[4:8]

res = sutherland_cohen(x1, y1, x2, y2, xmin, ymin, xmax, ymax)

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

plt.title("Алгоритм Сазерленда–Коэна")
plt.show()