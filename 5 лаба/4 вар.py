import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import os

n = int(input())

polygon = []
for i in range(n):
    x, y = map(int, input().split())
    polygon.append((x, y))

ordered_edges = [
    (polygon[1], polygon[2]),
    (polygon[3], polygon[4]),
    (polygon[0], polygon[1]),
    (polygon[2], polygon[3]),
    (polygon[4], polygon[0])
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
ax.set_title("XOR с перегородкой")

def draw_steps():
    img.fill(0)
    
    for p1, p2 in ordered_edges:
        x1, y1 = p1
        x2, y2 = p2
        
        if y1 == y2:
            continue
        
        if y1 < y2:
            y_start, y_end = y1, y2
            x_start, x_end = x1, x2
        else:
            y_start, y_end = y2, y1
            x_start, x_end = x2, x1
            
        dx = (x_end - x_start) / (y_end - y_start)
        cur_x = float(x_start)
        
        for y in range(int(y_start), int(y_end)):
            if 0 <= y < height:
                x_int = int(cur_x + 0.5)
                
                if 0 <= x_int < width:
                    img[y, x_int:] = 1 - img[y, x_int:]
            
            cur_x += dx
        
        yield img.copy()

step_generator = draw_steps()
step_counter = 0

save_dir = os.path.dirname(os.path.abspath(__file__))

def on_key(event):
    global step_counter
    
    if event.key == ' ':
        try:
            frame = next(step_generator)
            im.set_data(frame)
            fig.canvas.draw_idle()
            
            step_counter += 1
            filename = os.path.join(save_dir, f"step_{step_counter}.png")

            fig.savefig(filename)

            print(f"Сохранено: {filename}")
        
        except StopIteration:
            print("оп оп")

fig.canvas.mpl_connect('key_press_event', on_key)

plt.show()


# 5
# 10 150
# 20 80
# 50 100
# 90 10
# 150 150