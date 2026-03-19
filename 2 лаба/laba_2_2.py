import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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

WIDTH = 20
HEIGHT = 10

paddle_h = 3
paddle_speed = 0.5
ball_speed = 0.1

left_y = 0
right_y = 0

ball = np.array([[0.0, 0.0, 1.0]])

vx = ball_speed
vy = ball_speed

delay_frames = 0
DELAY = 60

keys = {"ц":False,"ы":False,"up":False,"down":False}

def transform(T, obj):
    new_obj = []
    for p in obj:
        P = np.array([[p[0]], [p[1]], [p[2]]])
        res = multiply(T, P)
        new_obj.append([res[0,0], res[1,0], res[2,0]])
    return np.array(new_obj)

def reset_ball(start=False):
    global ball, vx, vy, delay_frames
    
    ball = np.array([[0.0,0.0,1.0]])
    
    vx = np.random.choice([-ball_speed,ball_speed])
    vy = np.random.choice([-ball_speed,ball_speed])

    if start:
        delay_frames = 0
    else:
        delay_frames = DELAY

def update_paddles():
    global left_y, right_y
    
    if keys["ц"]:
        left_y = transform(move_y(paddle_speed), [[0,left_y,1]])[0][1]
    if keys["ы"]:
        left_y = transform(move_y(-paddle_speed), [[0,left_y,1]])[0][1]
        
    if keys["up"]:
        right_y = transform(move_y(paddle_speed), [[0,right_y,1]])[0][1]
    if keys["down"]:
        right_y = transform(move_y(-paddle_speed), [[0,right_y,1]])[0][1]
    
    min_y = -HEIGHT/2 + paddle_h/2
    max_y = HEIGHT/2 - paddle_h/2

    if left_y < min_y:
        left_y = min_y
    if left_y > max_y:
        left_y = max_y

    if right_y < min_y:
        right_y = min_y
    if right_y > max_y:
        right_y = max_y

def update_ball():
    global ball, vx, vy, delay_frames
    
    if delay_frames > 0:
        delay_frames -= 1
        return
    
    T = multiply(move_x(vx), move_y(vy))
    ball[:] = transform(T, ball)
    
    x, y = ball[0][0], ball[0][1]
    
    if y >= HEIGHT/2 or y <= -HEIGHT/2:
        vy = -vy
    
    if x <= -WIDTH/2+1:
        if abs(y - left_y) <= paddle_h/2:
            vx = -vx
        else:
            reset_ball()
    
    if x >= WIDTH/2-1:
        if abs(y - right_y) <= paddle_h/2:
            vx = -vx
        else:
            reset_ball()

def draw():
    ax.clear()
    ax.set_axis_off()
    
    ax.set_xlim(-WIDTH/2 - 1, WIDTH/2 + 1)
    ax.set_ylim(-HEIGHT/2 - 1, HEIGHT/2 + 1)
    ax.set_aspect("equal")

    rect_x = [-WIDTH/2, WIDTH/2, WIDTH/2, -WIDTH/2, -WIDTH/2]
    rect_y = [-HEIGHT/2, -HEIGHT/2, HEIGHT/2, HEIGHT/2, -HEIGHT/2]
    ax.plot(rect_x, rect_y, 'k-', linewidth=2) 

    ax.plot([0, 0], [-HEIGHT/2, HEIGHT/2], 'k--', alpha=0.3)
    
    ax.plot([-WIDTH/2 + 1, -WIDTH/2 + 1],
            [left_y - paddle_h/2, left_y + paddle_h/2],
            linewidth=6, solid_capstyle='butt')
    
    ax.plot([WIDTH/2 - 1, WIDTH/2 - 1],
            [right_y - paddle_h/2, right_y + paddle_h/2],
            linewidth=6, solid_capstyle='butt')
    
    ax.plot(ball[0][0], ball[0][1], 'ro', markersize=8)
    
    fig.canvas.draw_idle()

def update(frame):
    update_paddles()
    update_ball()
    draw()

def key_press(event):
    if event.key in keys:
        keys[event.key] = True

def key_release(event):
    if event.key in keys:
        keys[event.key] = False

fig, ax = plt.subplots(figsize=(8,5))

fig.canvas.mpl_connect("key_press_event", key_press)
fig.canvas.mpl_connect("key_release_event", key_release)

reset_ball(start=True)

ani = FuncAnimation(fig, update, interval=20)

plt.show()