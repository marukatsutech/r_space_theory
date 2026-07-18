""" down quark model """
import numpy as np
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import tkinter as tk
from tkinter import ttk
from scipy.spatial.transform import Rotation
import mpl_toolkits.mplot3d.art3d as art3d
from mpl_toolkits.mplot3d import proj3d

""" Global variables """
phase_step_deg = -1.
phase_init_a = 180.
phase_init_b = 0.
offset_scale = 0.5
size_phase_circle = 1.

color_a = "red"
color_a_path = "pink"
line_width1 = 2.
angle_a = -45.

color_b = "red"
color_b_path = "lime"
line_width2 = 1.
angle_b = -135.

""" Animation control """
is_play = False
is_rotation_1 = False
is_rotation_2 = False

""" Axis vectors """
vector_x_axis = np.array([1., 0., 0.])
vector_y_axis = np.array([0., 1., 0.])
vector_z_axis = np.array([0., 0., 1.])

""" Create figure and axes """
title_ax0 = "down quark model"
title_tk = title_ax0

x_min = -2.
x_max = 2.
y_min = -2.
y_max = 2.
z_min = -2.
z_max = 2.

fig = Figure()
ax0 = fig.add_subplot(111, projection="3d")
ax0.set_box_aspect((4, 4, 4))
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
canvas.get_tk_widget().pack(expand=True, fill="both")

toolbar = NavigationToolbar2Tk(canvas, root)
canvas.get_tk_widget().pack()

""" Global objects of Tkinter """


""" Classes and functions """


class Counter:
    def __init__(self, is3d=None, ax=None, xy=None, z=None, label=""):
        self.is3d = is3d if is3d is not None else False
        self.ax = ax
        self.x, self.y = xy[0], xy[1]
        self.z = z if z is not None else 0
        self.label = label

        self.count = 0

        if not is3d:
            self.txt_step = self.ax.text(self.x, self.y, self.label + str(self.count))
        else:
            self.txt_step = self.ax.text2D(self.x, self.y, self.label + str(self.count))
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


class FirstRotation:
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

        self.precession_axis = np.array([0., 0., 1.])
        self.precession_center = np.array([0., 0., 1. / np.sqrt(2)])
        self.precession_base_0 = np.array([1., 0., 0.])
        self.precession_base_1 = np.array([0., 1., 0.])
        self.radius_precession = 1. / np.sqrt(2)
        self.precession_point_1 = np.array([1. / np.sqrt(2), 0., 1. / np.sqrt(2)])
        self.precession_point_2 = np.array([0., - 1. / np.sqrt(2), 1. / np.sqrt(2)])
        self.precession_point_3 = np.array([- 1. / np.sqrt(2), 0., 1. / np.sqrt(2)])
        self.precession_point_4 = np.array([0., 1. / np.sqrt(2), 1. / np.sqrt(2)])

        # --- Rotation State ---
        self.rotated_angle = 0.0

        # --- Quivers ---
        self.quiver_obj_rotation_vector = None
        self.quiver_obj_precession_axis = None

        # --- Circles ---
        self.num_points_circle = 100
        self.theta = np.linspace(0., 2. * np.pi, self.num_points_circle)

        circle_phase_points = np.array([
            (np.cos(t) * self.phase_base_0 + np.sin(t) * self.phase_base_1) * self.radius_phase
            for t in self.theta
        ])
        self.circle_phase, = self.ax.plot(circle_phase_points[:, 0],
                                          circle_phase_points[:, 1],
                                          circle_phase_points[:, 2],
                                          linewidth=2, linestyle="-", color=self.color)

        circle_precession_points = np.array([
            (np.cos(t) * self.precession_base_0 + np.sin(t) * self.precession_base_1) * self.radius_precession
            for t in self.theta
        ])
        self.circle_precession, = self.ax.plot(circle_precession_points[:, 0] + self.precession_center[0],
                                               circle_precession_points[:, 1] + self.precession_center[1],
                                               circle_precession_points[:, 2] + self.precession_center[2],
                                               linewidth=1, linestyle="-", color="magenta")
        # --- Lines ---
        line_1 = zip(self.origin, self.precession_point_1)
        line_2 = zip(self.origin, self.precession_point_2)
        line_3 = zip(self.origin, self.precession_point_3)
        line_4 = zip(self.origin, self.precession_point_4)

        self.plt_cone_1, = self.ax.plot(*line_1, linewidth=1, linestyle="-", color="magenta")
        u, v, w = self.precession_point_1[0], self.precession_point_1[1], self.precession_point_1[2]
        self.marker_end_1, = self.ax.plot(u, v, w, marker="o", markersize=3, color="magenta")
        self.plt_cone_2, = self.ax.plot(*line_2, linewidth=1, linestyle="-", color="magenta")
        u, v, w = self.precession_point_2[0], self.precession_point_2[1], self.precession_point_2[2]
        self.marker_end_2, = self.ax.plot(u, v, w, marker="o", markersize=3, color="magenta")
        self.plt_cone_3, = self.ax.plot(*line_3, linewidth=1, linestyle="-", color="magenta")
        u, v, w = self.precession_point_3[0], self.precession_point_3[1], self.precession_point_3[2]
        self.marker_end_3, = self.ax.plot(u, v, w, marker="o", markersize=3, color="magenta")
        self.plt_cone_4, = self.ax.plot(*line_4, linewidth=1, linestyle="-", color="magenta")
        u, v, w = self.precession_point_4[0], self.precession_point_4[1], self.precession_point_4[2]
        self.marker_end_4, = self.ax.plot(u, v, w, marker="o", markersize=3, color="magenta")

        self.text_1 = ax.text(self.precession_point_1[0], self.precession_point_1[1], self.precession_point_1[2], "1",
                              fontsize=12)
        self.text_2 = ax.text(self.precession_point_2[0], self.precession_point_2[1], self.precession_point_2[2], "2",
                              fontsize=12)
        self.text_3 = ax.text(self.precession_point_3[0], self.precession_point_3[1], self.precession_point_3[2], "3",
                              fontsize=12)
        self.text_4 = ax.text(self.precession_point_4[0], self.precession_point_4[1], self.precession_point_4[2], "4",
                              fontsize=12)

        # --- Initialize ---
        self.rotate_rotation_vector(np.pi / 4., self.vector_y_axis)

        self.update_diagrams()

    def update_diagrams(self):
        # --- Quivers ---
        if self.quiver_obj_rotation_vector:
            self.quiver_obj_rotation_vector.remove()

        if self.quiver_obj_precession_axis:
            self.quiver_obj_precession_axis.remove()

        self.quiver_obj_rotation_vector = self.ax.quiver(
            self.origin[0], self.origin[1], self.origin[2],
            self.rotation_vector[0], self.rotation_vector[1], self.rotation_vector[2],
            length=1, color=self.color, linewidth=3,
            arrow_length_ratio=0.2, normalize=True, ls="-"
        )

        self.quiver_obj_precession_axis = self.ax.quiver(
            self.origin[0], self.origin[1], self.origin[2],
            self.precession_axis[0], self.precession_axis[1], self.precession_axis[2],
            length=1, color="magenta", linewidth=1,
            arrow_length_ratio=0.2, normalize=True, ls="-."
        )

        # --- Circles ---
        circle_phase_points = np.array([
            (np.cos(t) * self.phase_base_0 + np.sin(t) * self.phase_base_1) * self.radius_phase
            for t in self.theta
        ])

        self.circle_phase.set_data_3d(circle_phase_points[:, 0] + self.origin[0],
                                      circle_phase_points[:, 1] + self.origin[1],
                                      circle_phase_points[:, 2] + self.origin[2],
                                      )

        circle_precession_points = np.array([
            (np.cos(t) * self.precession_base_0 + np.sin(t) * self.precession_base_1) * self.radius_precession
            for t in self.theta
        ])

        self.circle_precession.set_data_3d(circle_precession_points[:, 0] + self.precession_center[0],
                                           circle_precession_points[:, 1] + self.precession_center[1],
                                           circle_precession_points[:, 2] + self.precession_center[2],
                                           )

        # --- Lines ---
        line_1 = zip(self.origin, self.precession_point_1)
        line_2 = zip(self.origin, self.precession_point_2)
        line_3 = zip(self.origin, self.precession_point_3)
        line_4 = zip(self.origin, self.precession_point_4)
        self.plt_cone_1.set_data_3d(*line_1)
        u, v, w = self.precession_point_1[0], self.precession_point_1[1], self.precession_point_1[2]
        self.marker_end_1.set_data_3d([u], [v], [w])

        self.plt_cone_2.set_data_3d(*line_2)
        u, v, w = self.precession_point_2[0], self.precession_point_2[1], self.precession_point_2[2]
        self.marker_end_2.set_data_3d([u], [v], [w])

        self.plt_cone_3.set_data_3d(*line_3)
        u, v, w = self.precession_point_3[0], self.precession_point_3[1], self.precession_point_3[2]
        self.marker_end_3.set_data_3d([u], [v], [w])

        self.plt_cone_4.set_data_3d(*line_4)
        u, v, w = self.precession_point_4[0], self.precession_point_4[1], self.precession_point_4[2]
        self.marker_end_4.set_data_3d([u], [v], [w])

        # --- Texts  ---
        self.text_1.set_position_3d(self.precession_point_1)
        self.text_2.set_position_3d(self.precession_point_2)
        self.text_3.set_position_3d(self.precession_point_3)
        self.text_4.set_position_3d(self.precession_point_4)

    def rotate_rotation_vector(self, angle, vector):
        rot_matrix = Rotation.from_rotvec(angle * vector)
        self.rotation_vector = rot_matrix.apply(self.rotation_vector)
        self.phase_base_0 = rot_matrix.apply(self.phase_base_0)
        self.phase_base_1 = rot_matrix.apply(self.phase_base_1)
        self.update_diagrams()

    def precess_rotation_vector(self, angle):
        rot_matrix = Rotation.from_rotvec(angle * - self.precession_axis)
        self.rotation_vector = rot_matrix.apply(self.rotation_vector)
        self.phase_base_0 = rot_matrix.apply(self.phase_base_0)
        self.phase_base_1 = rot_matrix.apply(self.phase_base_1)
        self.update_diagrams()

    def precess_axis_around_z(self, angle):
        sin_theta = 1.0 / np.sqrt(2)
        spin_angle = - angle / sin_theta

        # 1. First, rotate the object around its current precession axis (self‑rotation)
        rot_spin = Rotation.from_rotvec(spin_angle * self.precession_axis)

        # 2. Apply the total rotation to all components of the cone geometry.
        z_axis = np.array([0., 0., 1.])
        rot_precess = Rotation.from_rotvec(angle * z_axis)

        # combine the two rotations (self‑rotation followed by precession)
        total_rot = rot_precess * rot_spin

        # Apply the combined rotation to all elements of the cone structure
        self.rotation_vector = total_rot.apply(self.rotation_vector)
        self.phase_base_0 = total_rot.apply(self.phase_base_0)
        self.phase_base_1 = total_rot.apply(self.phase_base_1)

        self.precession_axis = total_rot.apply(self.precession_axis)
        self.precession_center = total_rot.apply(self.precession_center)
        self.precession_base_0 = total_rot.apply(self.precession_base_0)
        self.precession_base_1 = total_rot.apply(self.precession_base_1)

        self.precession_point_1 = total_rot.apply(self.precession_point_1)
        self.precession_point_2 = total_rot.apply(self.precession_point_2)
        self.precession_point_3 = total_rot.apply(self.precession_point_3)
        self.precession_point_4 = total_rot.apply(self.precession_point_4)

        self.update_diagrams()

    def rotate_all(self, angle, vector):
        rot_matrix = Rotation.from_rotvec(angle * vector)

        self.rotation_vector = rot_matrix.apply(self.rotation_vector)
        self.phase_base_0 = rot_matrix.apply(self.phase_base_0)
        self.phase_base_1 = rot_matrix.apply(self.phase_base_1)

        self.precession_axis = rot_matrix.apply(self.precession_axis)
        self.precession_center = rot_matrix.apply(self.precession_center)
        self.precession_base_0 = rot_matrix.apply(self.precession_base_0)
        self.precession_base_1 = rot_matrix.apply(self.precession_base_1)

        self.precession_point_1 = rot_matrix.apply(self.precession_point_1)
        self.precession_point_2 = rot_matrix.apply(self.precession_point_2)
        self.precession_point_3 = rot_matrix.apply(self.precession_point_3)
        self.precession_point_4 = rot_matrix.apply(self.precession_point_4)

        self.update_diagrams()


class SecondRotation:
    def __init__(self, ax):
        self.ax = ax

        self.origin = np.array([0., 0., 0.])
        self.vector_x_axis = np.array([1., 0., 0.])
        self.vector_y_axis = np.array([0., 1., 0.])
        self.vector_z_axis = np.array([0., 0., 1.])

        self.precession_axis = np.array([0., 0., 1.])
        self.precession_center = np.array([0., 0., 1. / np.sqrt(2)])
        self.precession_base_0 = np.array([1., 0., 0.])
        self.precession_base_1 = np.array([0., 1., 0.])
        self.radius_precession = 1. / np.sqrt(2)

        self.rotated_angle = 0.0

        # --- Quivers ---
        self.quiver_obj_precession_axis = None

        # --- Circles ---
        self.num_points_circle = 100
        self.theta = np.linspace(0., 2. * np.pi, self.num_points_circle)

        circle_precession_points = np.array([
            (np.cos(t) * self.precession_base_0 + np.sin(t) * self.precession_base_1) * self.radius_precession
            for t in self.theta
        ])
        self.circle_precession, = self.ax.plot(circle_precession_points[:, 0] + self.precession_center[0],
                                               circle_precession_points[:, 1] + self.precession_center[1],
                                               circle_precession_points[:, 2] + self.precession_center[2],
                                               linewidth=2, linestyle="-", color="gray")

        # --- Initialize ---
        self.update_diagrams()

    def update_diagrams(self):
        # --- Quivers ---
        if self.quiver_obj_precession_axis:
            self.quiver_obj_precession_axis.remove()

        self.quiver_obj_precession_axis = self.ax.quiver(
            self.origin[0], self.origin[1], self.origin[2],
            self.precession_axis[0], self.precession_axis[1], self.precession_axis[2],
            length=1, color="gray", linewidth=2,
            arrow_length_ratio=0.2, normalize=True, ls="-."
        )

        # --- Circles ---
        circle_precession_points = np.array([
            (np.cos(t) * self.precession_base_0 + np.sin(t) * self.precession_base_1) * self.radius_precession
            for t in self.theta
        ])

        self.circle_precession.set_data_3d(circle_precession_points[:, 0] + self.precession_center[0],
                                           circle_precession_points[:, 1] + self.precession_center[1],
                                           circle_precession_points[:, 2] + self.precession_center[2],
                                           )

    def rotate_all(self, angle, vector):
        rot_matrix = Rotation.from_rotvec(angle * vector)

        self.precession_axis = rot_matrix.apply(self.precession_axis)
        self.precession_center = rot_matrix.apply(self.precession_center)
        self.precession_base_0 = rot_matrix.apply(self.precession_base_0)
        self.precession_base_1 = rot_matrix.apply(self.precession_base_1)

        self.update_diagrams()

    def get_precession_axis(self):
        return self.precession_axis


def rotate_1():
    global is_play, is_rotation_1, is_rotation_2
    if not is_rotation_1 and not is_play:
        first_rotation.rotated_angle = 0.0

    is_play = True
    is_rotation_1 = True
    is_rotation_2 = False


def rotate_2():
    global is_play, is_rotation_1, is_rotation_2
    if not is_rotation_2 and not is_play:
        second_rotation.rotated_angle = 0.0

    is_play = True
    is_rotation_2 = True
    is_rotation_1 = False


def create_parameter_setter():
    frm_rotation = ttk.Labelframe(root, relief="ridge", text="Rotation", labelanchor="n")
    frm_rotation.pack(side="left", fill=tk.Y)
    btn_rotation_1 = tk.Button(frm_rotation, text="Rotation 1", command=rotate_1)
    btn_rotation_1.pack(side="left")
    btn_rotation_2 = tk.Button(frm_rotation, text="Rotation 2", command=rotate_2)
    btn_rotation_2.pack(side="left")


def create_animation_control():
    frm_anim = ttk.Labelframe(root, relief="ridge", text="Animation", labelanchor="n")
    frm_anim.pack(side="left", fill=tk.Y)
    btn_play = tk.Button(frm_anim, text="Play/Pause", command=switch)
    btn_play.pack(side="left")
    btn_reset = tk.Button(frm_anim, text="Reset", command=reset)
    btn_reset.pack(side="left")


def create_center_lines():
    ln_axis_x = art3d.Line3D([x_min, x_max], [0., 0.], [0., 0.], color="gray", ls="-.", linewidth=1)
    ax0.add_line(ln_axis_x)
    ln_axis_y = art3d.Line3D([0., 0.], [y_min, y_max], [0., 0.], color="gray", ls="-.", linewidth=1)
    ax0.add_line(ln_axis_y)
    ln_axis_z = art3d.Line3D([0., 0.], [0., 0.], [z_min, z_max], color="gray", ls="-.", linewidth=1)
    ax0.add_line(ln_axis_z)


def draw_static_diagrams():
    create_center_lines()


def update_diagrams():
    pass


def reset():
    global is_play, is_rotation_1, is_rotation_2
    cnt.reset()
    first_rotation.rotated_angle = 0.0
    second_rotation.rotated_angle = 0.0
    is_play = False
    is_rotation_1 = False
    is_rotation_2 = False


def switch():
    global is_play
    is_play = not is_play


def update(f):
    global is_play, is_rotation_1, is_rotation_2
    if is_play:
        cnt.count_up()

        # --- Rotation 1 animation control ---
        if is_rotation_1:
            step_angle = np.pi / 90
            target_angle = np.pi / 2

            if first_rotation.rotated_angle + step_angle >= target_angle:
                step_angle = target_angle - first_rotation.rotated_angle
                first_rotation.precess_rotation_vector(step_angle)
                first_rotation.rotated_angle += step_angle

                is_play = False
                is_rotation_1 = False
            else:
                first_rotation.precess_rotation_vector(step_angle)
                first_rotation.rotated_angle += step_angle

        # --- Rotation 2 animation control  ---
        elif is_rotation_2:
            step_angle = -np.pi / 90   # Orbital (rolling) speed per step

            # Due to geometric constraints (orbital + spin), this is the orbital angle at the moment
            # when the blue arrow points vertically upward.
            # Computed value: -pi / (2 * sqrt(2)) ≒ -63.64°
            target_angle = -np.pi / (2.0 * np.sqrt(2.0))

            if second_rotation.rotated_angle + step_angle <= target_angle:
                step_angle = target_angle - second_rotation.rotated_angle
                first_rotation.precess_axis_around_z(step_angle)
                second_rotation.rotated_angle += step_angle

                is_play = False
                is_rotation_2 = False
            else:
                first_rotation.precess_axis_around_z(step_angle)
                second_rotation.rotated_angle += step_angle

        update_diagrams()


""" main loop """
if __name__ == "__main__":
    cnt = Counter(ax=ax0, is3d=True, xy=np.array([x_min, y_max]), z=z_max, label="Step=")
    draw_static_diagrams()
    create_parameter_setter()

    first_rotation = FirstRotation(ax0, "blue")
    first_rotation.rotate_all(- np.pi / 4, vector_y_axis)
    second_rotation = SecondRotation(ax0)
    second_rotation.rotate_all(np.pi / 4, vector_y_axis)

    plt_dummy1 = ax0.plot(0, 0, 0, color="magenta", linewidth=1, label="1st precession")
    plt_dummy2 = ax0.plot(0, 0, 0, color="gray", linewidth=2, label="2nd precession")
    ax0.legend(loc='lower right', fontsize=8)

    anim = animation.FuncAnimation(fig, update, interval=100, save_count=100)
    root.mainloop()