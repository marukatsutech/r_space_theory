# Double rotation
import numpy as np
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import tkinter as tk
import matplotlib.patches as patches


def update_trail():
    global curve
    a0 = r0 * np.cos(- theta + np.pi / 2.)
    b0 = r0 * np.sin(- theta + np.pi / 2.)
    a1 = a0 + r1 * np.cos(- theta * 2. + np.pi / 2.)
    b1 = b0 + r1 * np.sin(- theta * 2. + np.pi / 2.)
    curve.set_data(a1, b1)


def update_diagrams():
    global cnt, line0, arrow1, l0_x, l0_y, l1_x, l1_y, circle_d, tx_coin1
    tx_step.set_text(' Step=' + str(cnt))
    th0 = (theta0 + (2. * np.pi) / 360. * cnt) % (2. * np.pi)
    l0_x = r0 * np.cos(- th0 + np.pi / 2.)
    l0_y = r0 * np.sin(- th0 + np.pi / 2.)
    th1 = (theta0 + (2. * np.pi) / 360. * cnt * 2) % (2. * np.pi)
    l1_x = l0_x + r1 * np.cos(- th1 + np.pi / 2.)
    l1_y = l0_y + r1 * np.sin(- th1 + np.pi / 2.)
    line0.set_data([0., l0_x], [0., l0_y])
    arrow1.xy = [l1_x, l1_y]
    arrow1.set_position([l0_x, l0_y])
    circle_d.set_center([l0_x, l0_y])

    tx_theta0.set_text(' Theta0=' + str(round(cnt % 360)) + "deg")
    tx_theta1.set_text(' Theta1=' + str(round((cnt * 2) % 720)) + "deg")

    tx_coin1.set_rotation(- (cnt * 2) % 720)
    tx_coin1.set_position([l0_x, l0_y])


def set_r1(value):
    global r1
    r1 = float(value)
    update_diagrams()
    update_trail()


def switch():
    global is_play
    if is_play:
        is_play = False
    else:
        is_play = True


def update(f):
    global cnt
    if is_play:
        update_diagrams()
        cnt += 1


# Global variables
is_play = False

x_min = -4.5
x_max = 4.5
y_min = -4.5
y_max = 4.5

cnt = 0

num_of_points = 500

p0 = np.array([0., 0.])
r0 = 2.
theta0 = 0.
p1 = np.array([0., 2.])
r1 = 1.
p0_d = np.array([0., 2.])

# Generate figure and axes
title_ax0 = "2 coins (Double rotation)"
title_tk = title_ax0
fig = Figure()
ax0 = fig.add_subplot(111)
ax0.grid()
ax0.set_title(title_ax0)
ax0.set_xlabel('x')
ax0.set_ylabel('y')
ax0.set_xlim(x_min, x_max)
ax0.set_ylim(y_min, y_max)
ax0.set_aspect("equal")

# Generate items
tx_step = ax0.text(x_min, y_max * 0.9, " Step=" + str(0))
tx_theta0 = ax0.text(x_min, y_max * 0.8, " Theta0=" + str(0) + "deg")
tx_theta1 = ax0.text(x_min, y_max * 0.7, " Theta1=" + str(0) + "deg")
circle = patches.Circle(xy=p0, radius=1, fill=False, color='gray')
ax0.add_patch(circle)
circle_d = patches.Circle(xy=p0_d, radius=1, fill=False, color='red')
ax0.add_patch(circle_d)

x = np.linspace(x_min, x_max, num_of_points)

l0_x = r0 * np.cos(theta0 + np.pi / 2.)
l0_y = r0 * np.sin(theta0 + np.pi / 2.)
l1_x = l0_x + r1 * np.cos(theta0 * 2. + np.pi / 2.)
l1_y = l0_y + r1 * np.sin(theta0 * 2. + np.pi / 2.)
line0, = ax0.plot([0., l0_x], [0., l0_y], linewidth=2)
arrow1 = ax0.annotate('', xy=[l1_x, l1_y], xytext=[l0_x, l0_y],
                      arrowprops=dict(width=1, headwidth=6, headlength=6,
                                      facecolor='darkorange', edgecolor='darkorange'))


theta = np.linspace(0, 2 * np.pi, 100)

a0 = r0 * np.cos(- theta + np.pi / 2.)
b0 = r0 * np.sin(- theta + np.pi / 2.)
a1 = a0 + r1 * np.cos(- theta * 2. + np.pi / 2.)
b1 = b0 + r1 * np.sin(- theta * 2. + np.pi / 2.)
curve, = ax0.plot(a1, b1, linestyle=':')

tx_coin0 = ax0.text(0, 0, "10", fontsize=36, c='gray', ha='center', va='center')
tx_coin1 = ax0.text(0, 2, "10", fontsize=36, c='red', ha='center', va='center')

# Embed in Tkinter
root = tk.Tk()
root.title(title_tk)
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack(expand=True, fill='both')

btn = tk.Button(root, text="Play/Pause", command=switch)
btn.pack(side='left')

label_r1 = tk.Label(root, text="Arrow length")
label_r1.pack(side='left')
var_r1 = tk.StringVar(root)  # variable for spinbox-value
var_r1.set(str(r1))  # Initial value
s_r1 = tk.Spinbox(
    root, textvariable=var_r1, format="%.1f", from_=0., to=2., increment=0.1,
    command=lambda: set_r1(var_r1.get()), width=5
    )
s_r1.pack(side='left')

toolbar = NavigationToolbar2Tk(canvas, root)
canvas.get_tk_widget().pack()

# main loop
anim = animation.FuncAnimation(fig, update, interval=50, save_count=100)
root.mainloop()

