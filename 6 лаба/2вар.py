import os
import matplotlib.pyplot as plt

n = int(input())
points = []
for i in range(n):
    parts = input().split()
    x = int(parts[0])
    y = int(parts[1])
    points.append((x, y))

Q = points[0]
for p in points:
    if p[0] < Q[0]:
        Q = p
    elif p[0] == Q[0] and p[1] < Q[1]:
        Q = p

def dist(p):
    return (p[0] - Q[0])**2 + (p[1] - Q[1])**2

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

unique_points = []
for p in points:
    if p != Q and p not in unique_points:
        unique_points.append(p)

for i in range(len(unique_points)):
    for j in range(0, len(unique_points) - i - 1):
        p1 = unique_points[j]
        p2 = unique_points[j + 1]
        
        cp = cross(Q, p1, p2)
        
        need_swap = False
        if cp < 0:
            need_swap = True
        elif cp == 0 and dist(p1) > dist(p2):
            need_swap = True
            
        if need_swap:
            temp = unique_points[j]
            unique_points[j] = unique_points[j + 1]
            unique_points[j + 1] = temp

sorted_points = [Q]
for p in unique_points:
    sorted_points.append(p)

history = []
stack = []

for p in sorted_points:
    while len(stack) >= 2:
        last = stack[-1]
        prev = stack[-2]
        if cross(prev, last, p) <= 0:
            stack.pop()
            history.append((list(stack), p, "pop"))
        else:
            break
            
    stack.append(p)
    history.append((list(stack), p, "push"))

history.append((list(stack), None, "done"))

fig, ax = plt.subplots(figsize=(10, 6))

xs_all = []
ys_all = []
for p in points:
    xs_all.append(p[0])
    ys_all.append(p[1])

ax.scatter(xs_all, ys_all, color="gray", label="Исходные точки")
ax.set_title("Алгоритм Грэхема")

min_x = min(xs_all) if len(xs_all) > 0 else 0
max_x = max(xs_all) if len(xs_all) > 0 else 0
min_y = min(ys_all) if len(ys_all) > 0 else 0
max_y = max(ys_all) if len(ys_all) > 0 else 0

ax.set_xlim(min_x - 10, max_x + 10)
ax.set_ylim(min_y - 10, max_y + 10)

hull_line, = ax.plot([], [], color="red", linewidth=2, label="Оболочка")
stack_points = ax.scatter([], [], color="blue", s=80, label="Стек")
current_point_plot = ax.scatter([], [], color="green", s=100, label="Текущая точка")
ax.legend(loc="upper right")

save_dir = os.path.dirname(os.path.abspath(__file__))
current_step_index = 0

def update_plot(current_stack, current_p, action):
    if len(current_stack) > 1:
        hx = []
        hy = []
        for sp in current_stack:
            hx.append(sp[0])
            hy.append(sp[1])
        hx.append(current_stack[0][0])
        hy.append(current_stack[0][1])
        hull_line.set_data(hx, hy)
    else:
        hull_line.set_data([], [])

    if len(current_stack) > 0:
        stack_points.set_offsets(current_stack)
    else:
        stack_points.set_offsets([])

    if current_p is not None:
        current_point_plot.set_offsets([[current_p[0], current_p[1]]])
    else:
        current_point_plot.set_offsets([])

    ax.set_title(f"Шаг алгоритма: {action}")

def on_key(event):
    global current_step_index
    
    if event.key == ' ':
        if current_step_index < len(history):
            step_stack, step_p, action = history[current_step_index]
            
            if action == "done":
                ax.set_title("есссс")
                current_point_plot.set_offsets([]) 
            else:
                update_plot(step_stack, step_p, action)
                
            fig.canvas.draw_idle()
            
            filename = os.path.join(save_dir, f"step_{current_step_index + 1}.png")
            fig.savefig(filename)
            
            current_step_index += 1

fig.canvas.mpl_connect('key_press_event', on_key)
plt.show()

# 8
# 50 150
# 100 50
# 150 150
# 120 100
# 80 100
# 60 120
# 140 120
# 100 180