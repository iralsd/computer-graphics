import matplotlib.pyplot as plt
import numpy as np
import os

def get_code(x, y, xmin, ymin, xmax, ymax):
    # 1 - слева, 2 - справа, 3 - снизу,4 - сверху
    code = 0
    if x < xmin: code |= 1
    if x > xmax: code |= 2  
    if y < ymin: code |= 4   
    if y > ymax: code |= 8  
    return code

def sutherland_cohen(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    while True:
        c1 = get_code(x1, y1, xmin, ymin, xmax, ymax)
        c2 = get_code(x2, y2, xmin, ymin, xmax, ymax)

        if c1 == 0 and c2 == 0:
            return [(x1, y1), (x2, y2)]
        if (c1 & c2) != 0:
            return None

        c = c1 if c1 != 0 else c2

        if c & 8:  
            if y2 == y1:
                return None
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax
        elif c & 4:
            if y2 == y1:
                return None
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin
        elif c & 2:
            if x2 == x1:
                return None
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax
        elif c & 1: 
            if x2 == x1:
                return None
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin

        if c == c1:
            x1, y1 = x, y
        else:
            x2, y2 = x, y

current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, "input_2.txt")

if not os.path.exists(input_file):
    with open(input_file, "w") as f:
        f.write("-4 -4 4 4 -2 -6 5 2")

with open(input_file, "r") as f:
    data = list(map(float, f.read().split()))
    xmin, ymin, xmax, ymax = data[0:4]
    p1_orig = (data[4], data[5])
    p2_orig = (data[6], data[7])

res = sutherland_cohen(p1_orig[0], p1_orig[1], p2_orig[0], p2_orig[1], xmin, ymin, xmax, ymax)

limit = 10
plt.figure(figsize=(8, 8))
plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.axhline(0, color='black', linewidth=1)
plt.axvline(0, color='black', linewidth=1)

plt.plot([xmin, xmax, xmax, xmin, xmin], [ymin, ymin, ymax, ymax, ymin], 
         color='blue', linewidth=2, label='Окно отсечения')

plt.plot([p1_orig[0], p2_orig[0]], [p1_orig[1], p2_orig[1]], 
         color='gray', linestyle='--', label='Исходный отрезок')


if res:
    rx, ry = zip(*res)
    plt.plot(rx, ry, color='red', linewidth=3, label='Результат')
    plt.scatter(rx, ry, color='red', zorder=5)

plt.gca().set_aspect('equal')
plt.xlim(-limit, limit)
plt.ylim(-limit, limit)
plt.title("Алгоритм Сазерленда–Коэна")
plt.legend()
plt.show()