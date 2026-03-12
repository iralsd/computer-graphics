import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox

def multiply(T, P):
    return np.dot(T, P)

def move_x(n): 
    return np.array([
        [1, 0, n],
        [0, 1, 0],
        [0, 0, 1]
    ])

def move_y(m): 
    return np.array([
        [1, 0, 0],
        [0, 1, m],
        [0, 0, 1]
    ])

def reflect_ox():
    return np.array([
        [1,  0, 0],
        [0, -1, 0],
        [0,  0, 1]
    ])

def reflect_oy():
    return np.array([
        [-1, 0, 0],
        [ 0, 1, 0],
        [ 0, 0, 1]
    ])

def reflect_yx():
    return np.array([
        [0, 1, 0],
        [1, 0, 0],
        [0, 0, 1]
    ])

def scale_mat(sx, sy):
    return np.array([
        [sx, 0,  0],
        [0,  sy, 0],
        [0,  0,  1]
    ])

def rotate_mat(phi): 
    rad = np.radians(phi)
    c, s = np.cos(rad), np.sin(rad)
    return np.array([
        [c,   s, 0],
        [-s,  c, 0],
        [0,   0, 1]
    ])

def rotate_point_mat(x0, y0, phi): 
    t1 = np.array([
        [1, 0, -x0],
        [0, 1, -y0],
        [0, 0, 1]
    ])
    rad = np.radians(phi)
    c, s = np.cos(rad), np.sin(rad)
    r = np.array([
        [c,   s, 0],
        [-s,  c, 0],
        [0,   0, 1]
    ])
    t2 = np.array([
        [1, 0, x0],
        [0, 1, y0],
        [0, 0, 1]
    ])
    return multiply(t2, multiply(r, t1))

points = np.array([
    [0, 0, 1], [1, 1.73, 1], [0, 4.5, 1], [-1, 1.73, 1], [0, 0, 1],
    [0, 0, 1], [2, 0, 1], [3.46, 2.5, 1], [1, 1.73, 1], [0, 0, 1],
    [0, 0, 1], [1, -1.73, 1], [3.46, -2.5, 1], [2, 0, 1], [0, 0, 1],
    [0, 0, 1], [-1, -1.73, 1], [0, -4.5, 1], [1, -1.73, 1], [0, 0, 1],
    [0, 0, 1], [-2, 0, 1], [-3.46, -2.5, 1], [-1, -1.73, 1], [0, 0, 1],
    [0, 0, 1], [-1, 1.73, 1], [-3.46, 2.5, 1], [-2, 0, 1], [0, 0, 1]
])

original_points = points.copy()

val_n = val_m = val_sx = val_sy = val_phi = val_x0 = val_y0 = ""

def transform(T):
    global points
    new_points = []
    for p in points:
        P = np.array([[p[0]], [p[1]], [p[2]]])
        res = multiply(T, P)
        new_points.append([res[0,0], res[1,0], res[2,0]])
    points = np.array(new_points)
    draw()

def draw():
    ax.clear()
    ax.plot(points[:, 0], points[:, 1], 'b-', linewidth=2, label='Фигура', zorder=2)
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.5, zorder=0)
    
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    
    ax.plot(15, 0, marker=">", color="black", clip_on=False, zorder=3)
    ax.plot(0, 15, marker="^", color="black", clip_on=False, zorder=3)
    ax.text(14.2, -1.2, 'X', fontsize=12, fontweight='bold')
    ax.text(-1.2, 14.2, 'Y', fontsize=12, fontweight='bold')
    
    fig.canvas.draw_idle()

def apply_move(event):
    try:
        if val_n: transform(move_x(float(val_n)))
        if val_m: transform(move_y(float(val_m)))
    except: pass

def apply_scale(event):
    try:
        sx = float(val_sx) if val_sx else 1.0
        sy = float(val_sy) if val_sy else 1.0
        transform(scale_mat(sx, sy))
    except: pass

def apply_rot(event):
    try:
        if val_phi: transform(rotate_mat(float(val_phi)))
    except: pass

def apply_rot_p(event):
    try:
        if val_phi and val_x0 and val_y0:
            transform(rotate_point_mat(float(val_x0), float(val_y0), float(val_phi)))
    except: pass

def reset(event):
    global points; points = original_points.copy()
    box_n.set_val("")
    draw()

fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(bottom=0.32)

ax_n = plt.axes([0.1, 0.22, 0.04, 0.04]); box_n = TextBox(ax_n, "n: ")
ax_m = plt.axes([0.18, 0.22, 0.04, 0.04]); box_m = TextBox(ax_m, "m: ")
ax_btn_m = plt.axes([0.23, 0.22, 0.12, 0.04]); btn_m = Button(ax_btn_m, "Перенос", color='azure')

ax_sx = plt.axes([0.45, 0.22, 0.04, 0.04]); box_sx = TextBox(ax_sx, "sx: ")
ax_sy = plt.axes([0.53, 0.22, 0.04, 0.04]); box_sy = TextBox(ax_sy, "sy: ")
ax_btn_s = plt.axes([0.58, 0.22, 0.12, 0.04]); btn_s = Button(ax_btn_s, "Масштаб", color='azure')

ax_phi = plt.axes([0.1, 0.15, 0.04, 0.04]); box_phi = TextBox(ax_phi, "phi: ")
ax_btn_r = plt.axes([0.15, 0.15, 0.15, 0.04]); btn_r = Button(ax_btn_r, "Поворот (0,0)", color='honeydew')

ax_x0 = plt.axes([0.4, 0.15, 0.04, 0.04]); box_x0 = TextBox(ax_x0, "x0: ")
ax_y0 = plt.axes([0.48, 0.15, 0.04, 0.04]); box_y0 = TextBox(ax_y0, "y0: ")
ax_btn_rp = plt.axes([0.53, 0.15, 0.17, 0.04]); btn_rp = Button(ax_btn_rp, "Поворот отн. (x0,y0)", color='honeydew')

ax_ox = plt.axes([0.1, 0.08, 0.12, 0.04]); btn_ox = Button(ax_ox, "Отр. OX", color='mistyrose')
ax_oy = plt.axes([0.23, 0.08, 0.12, 0.04]); btn_oy = Button(ax_oy, "Отр. OY", color='mistyrose')
ax_yx = plt.axes([0.36, 0.08, 0.12, 0.04]); btn_yx = Button(ax_yx, "Отр. Y=X", color='mistyrose')
ax_res = plt.axes([0.65, 0.08, 0.2, 0.04]); btn_res = Button(ax_res, "СБРОС", color='tomato')
 
box_n.on_text_change(lambda t: globals().update(val_n=t))
box_m.on_text_change(lambda t: globals().update(val_m=t))
box_sx.on_text_change(lambda t: globals().update(val_sx=t))
box_sy.on_text_change(lambda t: globals().update(val_sy=t))
box_phi.on_text_change(lambda t: globals().update(val_phi=t))
box_x0.on_text_change(lambda t: globals().update(val_x0=t))
box_y0.on_text_change(lambda t: globals().update(val_y0=t))

btn_m.on_clicked(apply_move)
btn_s.on_clicked(apply_scale)
btn_r.on_clicked(apply_rot)
btn_rp.on_clicked(apply_rot_p)
btn_ox.on_clicked(lambda e: transform(reflect_ox()))
btn_oy.on_clicked(lambda e: transform(reflect_oy()))
btn_yx.on_clicked(lambda e: transform(reflect_yx()))
btn_res.on_clicked(reset)

draw()
plt.show()