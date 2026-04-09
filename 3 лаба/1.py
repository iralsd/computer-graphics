import matplotlib.pyplot as plt
import numpy as np
import os


def bresenham(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    if x1 >= x0:
        sx = 1
    else:
        sx = -1
    if y1 >= y0:
        sy = 1
    else:
        sy = -1

    if dy > dx:
        dx, dy = dy, dx
        is_steep = True
    else:
        is_steep = False
    d = 2 * dy - dx
    x, y = x0, y0

    for i in range(dx + 1):
        points.append((x, y))
        while d >= 0:
            if is_steep:
                x += sx
            else:
                y += sy
            d -= 2 * dx
            
        if is_steep:
            y += sy
        else:
            x += sx
        d += 2 * dy
        print(x,y, d)
    return points


input_file = "input.txt"

if not os.path.exists(input_file):
    with open(input_file, "w") as f:
        f.write("0 0 30 12")

with open(input_file, "r") as f:
    coords = list(map(int, f.read().split()))
    xa, ya, xb, yb = coords

bres_points = bresenham(xa, ya, xb, yb)

max_x = max(xa, xb, 30)
max_y = max(ya, yb, 15)

x_vals = np.arange(0, max_x + 1, 1)
y_vals = np.arange(0, max_y + 1, 1)

plt.figure(figsize=(10, 6))

plt.xticks(x_vals)
plt.yticks(y_vals)
plt.grid(True)
plt.minorticks_on()
plt.grid(which='minor', linestyle=':', linewidth=0.5)

plt.plot([xa, xb], [ya, yb], linewidth=2, color='red', alpha=0.5, label="Линия между точками A и B")

bx, by = zip(*bres_points)
plt.scatter(bx, by, s=60, color='black', label="Отрезок Брезенхэма")

plt.gca().set_aspect('equal')
plt.legend()
plt.show()