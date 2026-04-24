import matplotlib.pyplot as plt
import numpy as np
import os

def bresenham_circle(xc, yc, r):
    points = set()
    x = 0
    y = r

    d = 3 - 2 * r
    
    delta1 = 6
    delta2 = 10 - 4 * r

    while x <= y:
        points.update([
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x),
            (xc + y, yc - x), (xc - y, yc - x)
        ])

        if d < 0:#горизонтально
            d += delta1
            delta1 += 4
            delta2 += 4
        else:
            d += delta2
            delta1 += 4
            delta2 += 8
            y -= 1
        
        x += 1

    return list(points)


input_file = "input_circle.txt"

if not os.path.exists(input_file):
    with open(input_file, "w") as f:
        f.write("15 15 12")

with open(input_file, "r") as f:
    data = list(map(int, f.read().split()))
    xc, yc, r = data

bres_points = bresenham_circle(xc, yc, r)

theta = np.linspace(0, 2 * np.pi, 300)
x_circle = xc + r * np.cos(theta)
y_circle = yc + r * np.sin(theta)

limit = max(xc, yc) + r + 2
x_vals = np.arange(0, limit, 1)
y_vals = np.arange(0, limit, 1)

plt.figure(figsize=(8, 8))

plt.xticks(x_vals)
plt.yticks(y_vals)
plt.grid(True)
plt.minorticks_on()
plt.grid(which='minor', linestyle=':', linewidth=0.5)

plt.plot(x_circle, y_circle, linewidth=2, color='red', alpha=0.5, label="Стандартная окружность")

bx, by = zip(*bres_points)
plt.scatter(bx, by, s=60, color='black', label="Пиксели Брезенхэма")

plt.gca().set_aspect('equal')
plt.xlim(0, limit-1)
plt.ylim(0, limit-1)
plt.legend()
plt.show()