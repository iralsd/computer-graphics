import matplotlib.pyplot as plt
import numpy as np
import os


def bresenham(x0, y0, x1, y1):
    points = []
    # Разница координат (абсолютные значения dx и dy из тетради)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    # Определение направления шага (s1 и s2 в записях)
    sx = 1 if x1 >= x0 else -1
    sy = 1 if y1 >= y0 else -1
    # Если dy > dx, значит линия "крутая" (угол > 45 градусов)
    # В этом случае меняем роли осей (как в лекционном алгоритме)
    if dy > dx:
        dx, dy = dy, dx
        is_steep = True
    else:
        is_steep = False
    # Инициализация параметра ошибки d)
    d = 2 * dy - dx
    x, y = x0, y0

    for _ in range(dx + 1):
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

    return points


input_file = "input.txt"

if not os.path.exists(input_file):
    with open(input_file, "w") as f:
        f.write("0 0 30 12")

with open(input_file, "r") as f:
    coords = list(map(int, f.read().split()))
    xa, ya, xb, yb = coords

# Вычисляем точки
bres_points = bresenham(xa, ya, xb, yb)

# Определяем границы поля с запасом
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

plt.plot([xa, xb], [ya, yb], linewidth=2, color='red', alpha=0.5, label="Standard line")

# 3. Пиксели Брезенхэма
bx, by = zip(*bres_points)
plt.scatter(bx, by, s=60, color='black', label="Bresenham pixels")

plt.gca().set_aspect('equal')
plt.title(f"Bresenham Line from ({xa},{ya}) to ({xb},{yb})")
plt.legend()
plt.show()