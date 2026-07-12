""" Color charge model """
import numpy as np
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import tkinter as tk
from tkinter import ttk
from matplotlib.patches import Circle
import mpl_toolkits.mplot3d.art3d as art3d
from mpl_toolkits.mplot3d import proj3d

""" Global variables """

""" Animation control """
is_play = False

""" Axis vectors """
vector_x_axis = np.array([1., 0., 0.])
vector_y_axis = np.array([0., 1., 0.])
vector_z_axis = np.array([0., 0., 1.])

""" Other parameters """
r_x = 1.
r_y = 1.
r_z = 1.

k_x = 1.
k_y = 1.
k_z = 1.

phase_init_x_deg = 0.
phase_init_y_deg = 0.
phase_init_z_deg = 0.

dir_rot_x = 1.
dir_rot_y = 1.
dir_rot_z = 1.

is_show_spiral = True


""" Create figure and axes """
title_ax0 = "Color charge model"
title_tk = title_ax0

x_min = -1.5
x_max = 1.5
y_min = -1.5
y_max = 1.5
z_min = -1.5
z_max = 1.5

fig = Figure()
ax0 = fig.add_subplot(111, projection='3d')
ax0.set_box_aspect((1, 1, 1))
ax0.grid()
ax0.set_title(title_ax0)
ax0.set_xlabel("x")
ax0.set_ylabel("y")
ax0.set_zlabel("z")
ax0.set_xlim(x_min, x_max)
ax0.set_ylim(y_min, y_max)
ax0.set_zlim(z_min, z_max)

""" Embed in Tkinter """
root = tk.Tk()
root.title(title_tk)
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack(expand=True, fill='both')

toolbar = NavigationToolbar2Tk(canvas, root)
canvas.get_tk_widget().pack()

""" Global objects of Tkinter """
var_time_op = tk.IntVar()

""" Classes and functions """


class Counter:
    def __init__(self, is3d=None, ax=None, xy=None, z=None, label="", color=None):
        self.is3d = is3d if is3d is not None else False
        self.ax = ax
        self.x, self.y = xy[0], xy[1]
        self.z = z if z is not None else 0
        self.label = label
        self.color = color
        self.count = 0

        if not is3d:
            self.txt_step = self.ax.text(self.x, self.y, self.label + str(self.count), color=color)
        else:
            self.txt_step = self.ax.text2D(self.x, self.y, self.label + str(self.count), color=color)
            self.xz, self.yz, _ = proj3d.proj_transform(self.x, self.y, self.z, self.ax.get_proj())
            self.txt_step.set_position((self.xz, self.yz))

    def count_up(self):
        self.count += 1
        self.txt_step.set_text(self.label + str(self.count))

    def reset(self):
        self.count = 0
        self.txt_step.set_text(self.label + str(self.count))

    def get(self):
        return self.count


class Circle3d:
    def __init__(self, ax, x, y, z, r, direction, line_width, line_style, color, alpha):
        self.ax = ax
        self.x, self.y, self.z = x, y, z
        self.r = r
        self.direction = direction
        self.line_width = line_width
        self.line_style = line_style
        self.color = color
        self.alpha = alpha
        self.is_visible = True

        self.angle_space = np.arange(0, 360)
        self._update_diagram()

        self.plt_circle, = self.ax.plot(self.x_circle, self.y_circle, self.z_circle,
                                        linewidth=self.line_width, linestyle=self.line_style,
                                        color=self.color, alpha=self.alpha)

    def set_r(self, r):
        self.r = r
        self._update_diagram()

    def set_y(self, y):
        if self.direction == "y":
            self.x = y
        self._update_diagram()
        self.plt_circle.set_xdata(self.x_circle)
        self.plt_circle.set_ydata(self.y_circle)
        self.plt_circle.set_3d_properties(self.z_circle)

    def _update_diagram(self):
        if self.is_visible:
            r = self.r
        else:
            r = 0
        self.cos_data = r * np.cos(self.angle_space * np.pi / 180.) + self.x
        self.sin_data = r * np.sin(self.angle_space * np.pi / 180.) + self.y
        self.plain_data = self.angle_space * 0. + self.z

        if self.direction == "x":
            self.x_circle, self.y_circle, self.z_circle = self.plain_data, self.cos_data, self.sin_data
        elif self.direction == "y":
            self.x_circle, self.y_circle, self.z_circle = self.cos_data, self.plain_data, self.sin_data
        else:  # "z"
            self.x_circle, self.y_circle, self.z_circle = self.cos_data, self.sin_data, self.plain_data

    def set_is_visible(self, value):
        self.is_visible = value
        self._update_diagram()


class WavedCircle3d:
    def __init__(self, ax, x, y, z, r, k, direction, line_width, line_style, color, alpha):
        self.ax = ax
        self.x, self.y, self.z = x, y, z
        self.r = r
        self.k = k
        self.direction = direction
        self.line_width = line_width
        self.line_style = line_style
        self.color = color
        self.alpha = alpha

        self.phase = 0.
        self.angle_space = np.arange(0, 360)

        self._calculate_coordinates()

        self.plt_circle, = self.ax.plot(self.x_circle, self.y_circle, self.z_circle,
                                        linewidth=self.line_width, linestyle=self.line_style,
                                        color=self.color, alpha=self.alpha)

        self.plt_circle_v, = self.ax.plot(self.x_circle_v, self.y_circle_v, self.z_circle_v,
                                          linewidth=self.line_width, linestyle=':',
                                          color='gray', alpha=self.alpha)

        self.plt_circle_hx, = self.ax.plot(self.x_circle_hx, self.y_circle_hx, self.z_circle_hx,
                                           linewidth=1.5, linestyle='-',
                                           color=self.color, alpha=0.5)

    def set_r(self, r):
        self.r = r
        self._update_diagram()

    def set_k(self, k):
        self.k = k
        self._update_diagram()

    def set_phase(self, phase_deg):
        self.phase = np.deg2rad(phase_deg)
        self._update_diagram()

    def _calculate_coordinates(self):
        amp = self.r * 0.2
        phi = self.angle_space * np.pi / 180.
        theta = self.k * phi + self.phase

        self.disp = self.r + amp * np.cos(theta)
        self.disp_v = amp * np.sin(theta)

        cos_waved = self.disp * np.cos(phi) + self.x
        sin_waved = self.disp * np.sin(phi) + self.y

        cos_flat = self.r * np.cos(phi) + self.x
        sin_flat = self.r * np.sin(phi) + self.y

        if self.direction == "x":
            self.x_circle, self.y_circle, self.z_circle = self.angle_space * 0. + self.z, cos_waved, sin_waved
            self.x_circle_v, self.y_circle_v, self.z_circle_v = (self.angle_space * 0. + self.z) + self.disp_v, cos_flat, sin_flat
            self.x_circle_hx, self.y_circle_hx, self.z_circle_hx = (self.angle_space * 0. + self.z) + self.disp_v, cos_waved, sin_waved

        elif self.direction == "y":
            self.x_circle, self.y_circle, self.z_circle = cos_waved, self.angle_space * 0. + self.z, sin_waved
            self.x_circle_v, self.y_circle_v, self.z_circle_v = cos_flat, (self.angle_space * 0. + self.z) + self.disp_v, sin_flat
            self.x_circle_hx, self.y_circle_hx, self.z_circle_hx = cos_waved, (self.angle_space * 0. + self.z) + self.disp_v, sin_waved

        else:  # "z"
            self.x_circle, self.y_circle, self.z_circle = cos_waved, sin_waved, self.angle_space * 0. + self.z
            self.x_circle_v, self.y_circle_v, self.z_circle_v = cos_flat, sin_flat, (self.angle_space * 0. + self.z) + self.disp_v
            self.x_circle_hx, self.y_circle_hx, self.z_circle_hx = cos_waved, sin_waved, (self.angle_space * 0. + self.z) + self.disp_v

    def _update_diagram(self):
        self._calculate_coordinates()

        self.plt_circle.set_xdata(self.x_circle)
        self.plt_circle.set_ydata(self.y_circle)
        self.plt_circle.set_3d_properties(self.z_circle)

        self.plt_circle_v.set_xdata(self.x_circle_v)
        self.plt_circle_v.set_ydata(self.y_circle_v)
        self.plt_circle_v.set_3d_properties(self.z_circle_v)

        self.plt_circle_hx.set_xdata(self.x_circle_hx)
        self.plt_circle_hx.set_ydata(self.y_circle_hx)
        self.plt_circle_hx.set_3d_properties(self.z_circle_hx)


class Arrow3d:
    def __init__(self, ax, x, y, z, u, v, w, color, line_width, line_style, arrow_length_ratio):
        self.ax = ax
        self.x, self.y, self.z = x, y, z
        self.u, self.v, self.w = u, v, w
        self.color = color
        self.line_width = line_width
        self.line_style = line_style
        self.arrow_length_ratio = arrow_length_ratio
        self.is_visible = True

        self.qvr = self.ax.quiver(self.x, self.y, self.z, self.u, self.v, self.w,
                                  length=1, color=self.color, normalize=False,
                                  linewidth=self.line_width, linestyle=self.line_style,
                                  arrow_length_ratio=self.arrow_length_ratio)

    def _update_quiver(self):
        if self.is_visible:
            u, v, w = self.u, self.v, self.w
        else:
            u, v, w = 0, 0, 0
        self.qvr.remove()
        self.qvr = self.ax.quiver(self.x, self.y, self.z, u, v, w,
                                  length=1, color=self.color, normalize=False,
                                  linewidth=self.line_width, linestyle=self.line_style,
                                  arrow_length_ratio=self.arrow_length_ratio)

    def set_vector(self, u, v, w):
        self.u, self.v, self.w = u, v, w
        self._update_quiver()

    def set_origin(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self._update_quiver()

    def get_vector(self):
        return np.array([self.u, self.v, self.w])

    def set_is_visible(self, value):
        self.is_visible = value
        self._update_quiver()


class LineVector:
    def __init__(self, ax, color):
        self.ax = ax
        self.color = color

        self.origin = np.array([0., 0., 0.])
        self.line_vector = np.array([1., 1., 1.])

        line_v = zip(self.origin, self.line_vector)
        self.plt_line_v, = self.ax.plot(*line_v, linewidth=1, linestyle="--", color=self.color)
        u, v, w = self.line_vector[0], self.line_vector[1], self.line_vector[2]
        self.marker_end, = self.ax.plot(u, v, w, marker="o", markersize=3, color=self.color, alpha=0.5)

    def set_vector(self, vector):
        self.line_vector = vector
        self._update_diagrams()

    def set_origin(self, vector):
        self.origin = vector
        self._update_diagrams()

    def get_vector(self):
        return self.line_vector

    def _update_diagrams(self):
        line_v = zip(self.origin, self.origin + self.line_vector)
        self.plt_line_v.set_data_3d(*line_v)
        u, v, w = self.line_vector[0] + self.origin[0], self.line_vector[1] + self.origin[1], self.line_vector[2] + self.origin[2]
        self.marker_end.set_data_3d([u], [v], [w])


def set_r_z(value):
    global r_z
    r_z = value
    circle_z.set_r(r_z)
    circle_y.set_y(r_z)
    circle_y.set_r(r_z * 0.2)
    arrow.set_origin(r_z, 0., 0.)
    phase_line.set_origin(np.array([r_z, 0., 0.]))
    update_diagrams()


def set_k_z(value):
    global k_z
    k_z = value
    arrow.set_vector(0., -0.0625 * k_z, 0.)
    update_diagrams()


def create_parameter_setter():
    frm_r = ttk.Labelframe(root, relief='ridge', text="Radius", labelanchor='n', width=100)
    frm_r.pack(side='left')

    lbl_r_z = tk.Label(frm_r, text="z")
    lbl_r_z.pack(side='left')
    var_r_z = tk.StringVar(root)
    var_r_z.set(str(r_z))
    spn_r_z = tk.Spinbox(
        frm_r, textvariable=var_r_z, format='%.1f', from_=-10, to=10, increment=0.1,
        command=lambda: set_r_z(float(var_r_z.get())), width=4
    )
    spn_r_z.pack(side='left')

    frm_k = ttk.Labelframe(root, relief='ridge', text="k (wave number)", labelanchor='n', width=100)
    frm_k.pack(side='left')

    lbl_k_z = tk.Label(frm_k, text="z")
    lbl_k_z.pack(side='left')
    var_k_z = tk.StringVar(root)
    var_k_z.set(str(k_z))
    spn_k_z = tk.Spinbox(
        frm_k, textvariable=var_k_z, format='%.1f', from_=-20, to=20, increment=0.1,
        command=lambda: set_k_z(float(var_k_z.get())), width=4
    )
    spn_k_z.pack(side='left')


def create_animation_controls():
    frm_anim = ttk.Labelframe(root, relief="ridge", text="Animation", labelanchor="n")
    frm_anim.pack(side="left", fill=tk.Y)
    btn_play = tk.Button(frm_anim, text="Play/Pause", command=switch)
    btn_play.pack(fill=tk.X)


def create_visual_controls():
    global is_show_spiral
    frm_visual = ttk.Labelframe(root, relief='ridge', text="Visual", labelanchor='n')
    frm_visual.pack(side='left', fill=tk.Y)

    def switch_spiral():
        global is_show_spiral
        is_show_spiral = not is_show_spiral
        if is_show_spiral:
            waved_circle_z.plt_circle_hx.set_visible(True)
            arrow.set_is_visible(True)
            circle_y.set_is_visible(True)
        else:
            waved_circle_z.plt_circle_hx.set_visible(False)
            arrow.set_is_visible(False)
            circle_y.set_is_visible(False)

    chk_spiral = tk.Checkbutton(frm_visual, text="Spiral", command=switch_spiral)
    chk_spiral.select()
    chk_spiral.pack(side='left')


def create_center_lines(ax, x_min, x_max, y_min, y_max, z_min, z_max):
    line_axis_x = art3d.Line3D([x_min, x_max], [0., 0.], [0., 0.], color='gray', ls='-.', linewidth=1)
    ax.add_line(line_axis_x)
    line_axis_y = art3d.Line3D([0., 0.], [y_min, y_max], [0., 0.], color='gray', ls='-.', linewidth=1)
    ax.add_line(line_axis_y)
    line_axis_z = art3d.Line3D([0., 0.], [0., 0.], [z_min, z_max], color='gray', ls='-.', linewidth=1)
    ax.add_line(line_axis_z)


def draw_static_diagrams():
    create_center_lines(ax0, -1., 1., y_min, y_max, z_min, z_max)
    c02 = Circle((0, 0), 1, ec='pink', fill=False, ls='-.')
    ax0.add_patch(c02)
    art3d.pathpatch_2d_to_3d(c02, z=0, zdir='z')

    quiver_obj = ax0.quiver(0., 0., 0., 0., 0., 1.,
        length=1, color='red', linewidth=3,
        arrow_length_ratio=0.2, normalize=True, ls='-'
    )


def update_diagrams():
    waved_circle_z.set_r(r_z)
    waved_circle_z.set_k(k_z)


def reset():
    global is_play
    cnt.reset()
    update_diagrams()


def switch():
    global is_play
    is_play = not is_play


def update(f):
    txt_parameter.set_text(fr"Radius={r_z}, k={k_z}")
    if is_play:
        cnt.count_up()
        phase = - cnt.get() * 6. * k_z
        waved_circle_z.set_phase(phase)
        phase_line.set_vector(np.array([0.2 * np.cos(np.deg2rad(phase)), 0., 0.2 * np.sin(np.deg2rad(phase))]))

        phase1 = - cnt.get() * 6.
        phase_line1.set_vector(np.array([r_z * np.cos(np.deg2rad(phase1)), r_z * np.sin(np.deg2rad(phase1)), 0.,]))

        update_diagrams()


""" main loop """
if __name__ == '__main__':
    cnt = Counter(ax=ax0, is3d=True, xy=np.array([x_min, y_max]), z=z_max, label="Step=")
    draw_static_diagrams()
    create_animation_controls()
    create_parameter_setter()
    create_visual_controls()

    circle_z = Circle3d(ax0, 0., 0., 0., 1., "z", 1, '-', 'darkred', 1)
    waved_circle_z = WavedCircle3d(ax0, 0., 0., 0., 1., 1., "z", 1., '-', 'red', 1)
    circle_y = Circle3d(ax0, 1., 0., 0., 0.2, "y", 1, '-', 'red', 1)

    arrow = Arrow3d(ax0, 1., 0., 0., 0., -0.0625, 0., 'red', 2, '-', 0.2)

    phase_line = LineVector(ax0, "red")
    phase_line.set_origin(np.array([1., 0., 0.,]))
    phase_line.set_vector(np.array([0.2, 0., 0.,]))

    phase_line1 = LineVector(ax0, "red")
    phase_line1.set_origin(np.array([0., 0., 0., ]))
    phase_line1.set_vector(np.array([1., 0., 0., ]))

    update_diagrams()

    txt_parameter = ax0.text2D(x_min, y_max, fr"Radius={r_z}, k={k_z}", fontsize="12")
    xz, yz, _ = proj3d.proj_transform(x_min + 0.5, y_max, z_max - 0.5, ax0.get_proj())
    txt_parameter.set_position((xz, yz))

    anim = animation.FuncAnimation(fig, update, interval=100, save_count=100)
    root.mainloop()