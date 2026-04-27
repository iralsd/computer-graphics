import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap

A, B, C, D, E = (10, 150), (20, 80), (50, 100), (90, 10), (150, 150)
polygon = [A, B, C, D, E]

ordered_edges = [
    (B, C),
    (D, E),
    (A, B),
    (C, D),
    (E, A)
]

width, height = 300, 200
img = np.zeros((height, width), dtype=np.uint8)

cmap = ListedColormap(["white", "darkgray"])
fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(img, cmap=cmap, vmin=0, vmax=1, aspect='auto')

xs = [p[0] for p in polygon] + [polygon[0][0]]
ys = [p[1] for p in polygon] + [polygon[0][1]]
ax.plot(xs, ys, color="black", linewidth=2)
ax.set_xlim(0, width)
ax.set_ylim(height, 0)
ax.set_title("Lab 5: XOR с перегородкой")

def draw_steps():
    for p1, p2 in ordered_edges:
        x1, y1 = p1
        x2, y2 = p2
        
        # Горизонтальное ребро
        if y1 == y2:
            y = y1
            x_left = int(min(x1, x2))
            if 0 <= y < height:
                img[y, x_left:] = 1 - img[y, x_left:]
                yield img.copy()
            continue
        
        # Определяем направление: true = вниз (y увеличивается)
        go_down = y2 > y1
        
        # Приводим к формату: y_low (верх) -> y_high (низ)
        if not go_down:
            x1, y1, x2, y2 = x2, y2, x1, y1
        
        dx = (x2 - x1) / (y2 - y1)
        
        # Канон: включаем y_min, исключаем y_max
        # Если ребро в оригинале шло вниз — y1 это верх, включаем его
        # Если ребро в оригинале шло вверх — y2 это верх (который стал y1 после сортировки)
        # НО! После сортировки y1 всегда верх. Правило: включаем y_low, исключаем y_high.
        # А для того чтобы вершина обработалась ровно 1 раз:
        # — если ребро идёт вниз (go_down=true):  range(y_low, y_high)
        # — если ребро идёт вверх (go_down=false): range(y_low+1, y_high+1)
        
        if go_down:
            y_start, y_end = y1, y2
            cur_x = x1
        else:
            y_start, y_end = y1 + 1, y2 + 1
            cur_x = x1 + dx
        
        for y in range(y_start, y_end):
            if y >= height:
                break
            x_int = int(round(cur_x))
            
            if 0 <= y < height and 0 <= x_int < width:
                img[y, x_int:] = 1 - img[y, x_int:]
            
            cur_x += dx
            yield img.copy()

    for _ in range(50):
        yield img.copy()

def update(frame):
    im.set_data(frame)
    return [im]

ani = FuncAnimation(fig, update, frames=draw_steps, interval=5, repeat=False, save_count=2000)
plt.show()