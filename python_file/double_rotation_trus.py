""" Double rotation (torus) """
import numpy as np
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import tkinter as tk
from tkinter import ttk
import mpl_toolkits.mplot3d.art3d as art3d
from mpl_toolkits.mplot3d import proj3d
from scipy.spatial.transform import Rotation

""" Global variables """
num = 32

""" Animation control """
is_play = False

""" Axis vectors """
vector_x_axis = np.array([1., 0., 0.])
vector_y_axis = np.array([0., 1., 0.])
vector_z_axis = np.array([0., 0., 1.])

""" Other parameters """
r_rotation_vector = 1.0
r_orbital = 0.5
rotation_vectors = []

""" Create figure and axes """
title_ax0 = "Double rotation (torus)"
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


class RotationVector:
    def __init__(self, ax, color):
        self.ax = ax
        self.color = color

        self.origin = np.array([0., 0., 0.])
        self.vector_x_axis = np.array([1., 0., 0.])
        self.vector_y_axis = np.array([0., 1., 0.])
        self.vector_z_axis = np.array([0., 0., 1.])

        self.rotation_vector = np.array([0., 0., 1.])
        self.phase_base_0 = np.array([1., 0., 0.])
        self.phase_base_1 = np.array([0., 1., 0.])
        self.radius_phase = 1.

        self.offset = np.array([0., 0., 0.])

        # --- Quivers ---
        self.quiver_obj_rotation_vector = None

        # --- Circles ---
        self.num_points_circle = 100
        self.theta = np.linspace(0., 2. * np.pi, self.num_points_circle)

        self.circle_phase, = self.ax.plot([], [], [], linewidth=0.5, linestyle="-", color=self.color)

        # --- Lines ---
        xs = [self.origin[0] + self.offset[0], self.phase_base_0[0] + self.offset[0]]
        ys = [self.origin[1] + self.offset[1], self.phase_base_0[1] + self.offset[1]]
        zs = [self.origin[2] + self.offset[2], self.phase_base_0[2] + self.offset[2]]

        self.plt_cone_1, = self.ax.plot(xs, ys, zs, linewidth=1, linestyle="-", color="magenta")
        u, v, w = self.phase_base_0[0] + self.offset[0], self.phase_base_0[1] + self.offset[1], self.phase_base_0[2] + self.offset[2]
        self.marker_end_1, = self.ax.plot([u], [v], [w], marker="o", markersize=3, color="magenta")

        # --- Initialize
        self.update_diagrams()

    def update_diagrams(self):
        # --- Quivers ---
        if self.quiver_obj_rotation_vector:
            self.quiver_obj_rotation_vector.remove()

        self.quiver_obj_rotation_vector = self.ax.quiver(
            self.origin[0] + self.offset[0], self.origin[1] + self.offset[1], self.origin[2] + self.offset[2],
            self.rotation_vector[0], self.rotation_vector[1], self.rotation_vector[2],
            length=1, color=self.color, linewidth=1,
            arrow_length_ratio=0.2, normalize=True, ls="-"
        )

        # --- Circles ---
        circle_phase_points = np.array([
            (np.cos(t) * self.phase_base_0 + np.sin(t) * self.phase_base_1) * self.radius_phase
            for t in self.theta
        ])

        self.circle_phase.set_data_3d(circle_phase_points[:, 0] + self.origin[0] + self.offset[0],
                                      circle_phase_points[:, 1] + self.origin[1] + self.offset[1],
                                      circle_phase_points[:, 2] + self.origin[2] + self.offset[2],
                                      )

        # --- Lines ---
        xs = [self.origin[0] + self.offset[0], self.phase_base_0[0] + self.offset[0]]
        ys = [self.origin[1] + self.offset[1], self.phase_base_0[1] + self.offset[1]]
        zs = [self.origin[2] + self.offset[2], self.phase_base_0[2] + self.offset[2]]
        self.plt_cone_1.set_data_3d(xs, ys, zs)

        u, v, w = self.phase_base_0[0] + self.offset[0], self.phase_base_0[1] + self.offset[1], self.phase_base_0[2] + self.offset[2]
        self.marker_end_1.set_data_3d([u], [v], [w])

    def rotate_all(self, angle, vector):
        rot_matrix = Rotation.from_rotvec(angle * vector)

        self.rotation_vector = rot_matrix.apply(self.rotation_vector)
        self.phase_base_0 = rot_matrix.apply(self.phase_base_0)
        self.phase_base_1 = rot_matrix.apply(self.phase_base_1)

        self.update_diagrams()

    def spin_phase(self, angle):
        rot_matrix = Rotation.from_rotvec(angle * self.rotation_vector)
        self.phase_base_0 = rot_matrix.apply(self.phase_base_0)
        self.phase_base_1 = rot_matrix.apply(self.phase_base_1)
        self.update_diagrams()

    def set_offset(self, offset):
        self.offset = offset
        self.update_diagrams()

    # マーカーの位置情報を取得
    def get_marker_position(self):
        return self.phase_base_0 + self.offset


class Orbital:
    def __init__(self, ax, radius, color):
        self.ax = ax
        self.radius = radius
        self.color = color

        self.num_points_circle = 100
        self.theta = np.linspace(0., 2. * np.pi, self.num_points_circle)

        self.circle, = self.ax.plot([], [], [], linewidth=1, linestyle="--", color=self.color)
        self.update_radius(self.radius)

    def update_radius(self, r):
        self.radius = r
        x = self.radius * np.cos(self.theta)
        y = self.radius * np.sin(self.theta)
        z = np.zeros_like(self.theta)
        self.circle.set_data_3d(x, y, z)


def set_radius_orbital(value):
    global r_orbital
    r_orbital = value
    update_diagrams()


def create_parameter_setter():
    frm_r_orbital = ttk.Labelframe(root, relief='ridge', text="Radius (orbital)", labelanchor='n')
    frm_r_orbital.pack(side='left', padx=5)
    var_r_orbital = tk.StringVar(root, value=str(r_orbital))
    spn_r_orbital = tk.Spinbox(
        frm_r_orbital, textvariable=var_r_orbital, format='%.1f', from_=-2.0, to=2.0, increment=0.1,
        command=lambda: set_radius_orbital(float(var_r_orbital.get())), width=5
    )
    spn_r_orbital.pack(side='left', padx=2)


def create_animation_controls():
    frm_anim = ttk.Labelframe(root, relief="ridge", text="Animation", labelanchor="n")
    frm_anim.pack(side="left", fill=tk.Y, padx=5)
    btn_play = tk.Button(frm_anim, text="Play/Pause", command=switch)
    btn_play.pack(fill=tk.X)


def create_center_lines(ax, x_min, x_max, y_min, y_max, z_min, z_max):
    line_axis_x = art3d.Line3D([x_min, x_max], [0., 0.], [0., 0.], color='gray', ls='-.', linewidth=1)
    ax.add_line(line_axis_x)
    line_axis_y = art3d.Line3D([0., 0.], [y_min, y_max], [0., 0.], color='gray', ls='-.', linewidth=1)
    ax.add_line(line_axis_y)
    line_axis_z = art3d.Line3D([0., 0.], [0., 0.], [z_min, z_max], color='gray', ls='-.', linewidth=1)
    ax.add_line(line_axis_z)


def draw_static_diagrams():
    create_center_lines(ax0, x_min, x_max, y_min, y_max, z_min, z_max)


def update_diagrams():
    orbital.update_radius(r_orbital)

    for ii, rotation_vector in enumerate(rotation_vectors):
        angle = 2 * np.pi * ii / num
        new_offset = np.array([r_orbital * np.cos(angle), r_orbital * np.sin(angle), 0.])
        rotation_vector.set_offset(new_offset)

    update_marker_connecting_line()
    canvas.draw_idle()


def update_marker_connecting_line():
    if len(rotation_vectors) == 0:
        return
    pts = [rv.get_marker_position() for rv in rotation_vectors]
    pts.append(pts[0])
    pts = np.array(pts)
    line_markers.set_data_3d(pts[:, 0], pts[:, 1], pts[:, 2])


def switch():
    global is_play
    is_play = not is_play


def update(f):
    if is_play:
        cnt.count_up()

        d_spin = 0.08

        for rotation_vector in rotation_vectors:
            rotation_vector.spin_phase(d_spin)

        update_diagrams()


""" main loop """
if __name__ == '__main__':
    cnt = Counter(ax=ax0, is3d=True, xy=np.array([x_min, y_max]), z=z_max, label="Step=")
    draw_static_diagrams()
    create_animation_controls()
    create_parameter_setter()

    orbital = Orbital(ax0, r_orbital, "gray")
    line_markers, = ax0.plot([], [], [], linewidth=2, linestyle="-", color="red", alpha=0.8)

    for ii in range(num):
        angle = 2 * np.pi * ii / num
        offset = np.array([r_orbital * np.cos(angle), r_orbital * np.sin(angle), 0.])

        rotation_vector = RotationVector(ax0, "blue")

        rotation_vector.rotate_all(-np.pi / 2, vector_y_axis)
        rotation_vector.rotate_all(np.pi / 4, vector_y_axis)
        rotation_vector.rotate_all(angle + np.pi / 2, vector_z_axis)

        phase_shift = (2 * np.pi * ii / num) * 1.0
        rotation_vector.spin_phase(phase_shift)

        rotation_vector.set_offset(offset)
        rotation_vectors.append(rotation_vector)

    update_diagrams()

    anim = animation.FuncAnimation(fig, update, interval=50, save_count=100)
    root.mainloop()