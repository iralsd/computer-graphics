import matplotlib.pyplot as plt
import numpy as np
import os

def polygon_orientation(poly): 
# смотрим на какой высоте сторона и насколько она сдвинулась по х перемножаем это и все произведения складываем
# удвоенная ориентированная площадь многоугольника
    s = 0 
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += (x2 - x1) * (y2 + y1)
    return s

def cyrus_beck(p0, p1, poly):
    x1, y1 = p0
    x2, y2 = p1
    dx, dy = x2 - x1, y2 - y1

    t_in = 0.0
    t_out = 1.0
    
    all_pe_points = [] # потенциально входящие
    all_pl_points = [] # потенциально покидающие

    orientation = polygon_orientation(poly)

    for i in range(len(poly)):
        p_curr = poly[i]
        p_next = poly[(i + 1) % len(poly)]

        ex = p_next[0] - p_curr[0]
        ey = p_next[1] - p_curr[1]
        
        # направление нормали вовне
        if orientation < 0:
            nx, ny = ey, -ex
        else:
            nx, ny = -ey, ex

        # вектор от начала стороны до отрезка
        wx = x1 - p_curr[0] 
        wy = y1 - p_curr[1]

        # num > 0 снаружи точка num < 0 внутри 
        num = wx * nx + wy * ny
        # den > 0 снаружу идет den  < 0 внутрь
        den = dx * nx + dy * ny

        if den == 0:
            if num > 0:
                return None, [], []
            continue
            
        t = -num / den
        intersect_point = (x1 + t * dx, y1 + t * dy)

        if den < 0: # ПВ
            t_in = max(t_in, t)
            all_pe_points.append(intersect_point)
        else: # ПП
            t_out = min(t_out, t)
            all_pl_points.append(intersect_point)

    if t_in > t_out:
        return None, all_pe_points, all_pl_points

    res = [
        (x1 + t_in * dx, y1 + t_in * dy),
        (x1 + t_out * dx, y1 + t_out * dy)
    ]
    return res, all_pe_points, all_pl_points


input_file = "input_1.txt"
if not os.path.exists(input_file):
    with open(input_file, "w") as f:
        f.write("0 5 -5 2 -3 -5 3 -5 5 2 -8 -1 8 4")

with open(input_file, "r") as f:
    data = list(map(float, f.read().split()))
    poly = [data[i:i+2] for i in range(0, 10, 2)]
    p0 = [data[10], data[11]]
    p1 = [data[12], data[13]]

res, pe_points, pl_points = cyrus_beck(p0, p1, poly)

limit = 10
vals = np.arange(-limit, limit + 1, 1)

plt.figure(figsize=(9, 9))
plt.xticks(vals)
plt.yticks(vals)
plt.grid(True)
plt.minorticks_on()
plt.grid(which='minor', linestyle=':', linewidth=0.5)

plt.axhline(0, color='black', linewidth=1)
plt.axvline(0, color='black', linewidth=1)

poly_draw = poly + [poly[0]]
px, py = zip(*poly_draw)
plt.plot(px, py, color='blue', linewidth=2, label='Окно')

plt.plot([p0[0], p1[0]], [p0[1], p1[1]], color='gray', linestyle='--', alpha=0.6, label='Исходный отрезок')

if pe_points:
    px_e, py_e = zip(*pe_points)
    plt.scatter(px_e, py_e, color='cyan', edgecolors='black', s=60, zorder=5, label='ПВ (потенциальный вход)')
if pl_points:
    px_l, py_l = zip(*pl_points)
    plt.scatter(px_l, py_l, color='orange', edgecolors='black', s=60, zorder=5, label='ПП (потенциальный выход)')

if res:
    rx, ry = zip(*res)
    plt.plot(rx, ry, color='red', linewidth=3, label='Отсеченный отрезок')
    plt.scatter(rx, ry, color='red', s=40, zorder=6)

plt.gca().set_aspect('equal')
plt.xlim(-limit, limit)
plt.ylim(-limit, limit)
plt.title("Алгоритм Цируса–Бека")
plt.legend(loc='upper right', fontsize='small')
plt.show()