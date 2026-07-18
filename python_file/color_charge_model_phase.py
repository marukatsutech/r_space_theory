""" Color charge model (vibration phase in Torus geometry) """
import numpy as np
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import tkinter as tk
from tkinter import ttk
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
r_rotation_vector = 1.0   # Major radius of the torus (R)
r_color_charge = 0.2      # Minor radius of the torus (r)

k = 1.0                   # Wave number (Initial value set to 1.0 for visual clarity)

ring_line = None

""" Create figure and axes """
title_ax0 = "Color charge model (Torus & Wave phase)"
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


class RotationVector:
    def __init__(self, ax, radius, color):
        self.ax = ax
        self.radius = radius
        self.color = color

        self.num_points_circle = 100
        self.theta = np.linspace(0., 2. * np.pi, self.num_points_circle)

        # Initial plot of the major circle (base ring)
        self.circle_r_vector, = self.ax.plot([], [], [], linewidth=1.5, linestyle="--", color=self.color)
        self.update_radius(self.radius)

    def update_radius(self, r):
        self.radius = r
        x = self.radius * np.cos(self.theta)
        y = self.radius * np.sin(self.theta)
        z = np.zeros_like(self.theta)
        self.circle_r_vector.set_data_3d(x, y, z)


class ColorCharge:
    def __init__(self, ax, radius, phi, phase, color):
        self.ax = ax
        self.radius = radius    # Minor radius
        self.phi = phi          # Position angle on the major circle (fixed)
        self.phase = phase      # Vibration/rotation phase
        self.color = color

        # Basis vectors forming the cross-sectional circle of the torus (normal vector is tangent to the ring)
        self.cos_p = np.cos(self.phi)
        self.sin_p = np.sin(self.phi)
        self.base_0 = np.array([self.cos_p, self.sin_p, 0.])  # Outward radial vector
        self.base_1 = np.array([0., 0., 1.])                  # Vertical z-axis vector

        self.num_points_circle = 60
        self.theta = np.linspace(0., 2. * np.pi, self.num_points_circle)

        # Create empty line objects
        self.circle_color, = self.ax.plot([], [], [], linewidth=1, linestyle="-", color=self.color, alpha=0.3)
        self.plt_phase, = self.ax.plot([], [], [], linewidth=1, linestyle="-", color=self.color)
        self.marker_end_1, = self.ax.plot([], [], [], marker="o", markersize=4, color=self.color)

    def update_geometry(self, r_large, r_small, current_phase):
        self.radius = r_small
        self.phase = current_phase

        # 1. Calculate the new center coordinates on the major circle
        center = np.array([r_large * self.cos_p, r_large * self.sin_p, 0.])

        # 2. Calculate the coordinates of the cross-sectional circle (minor circle of the torus)
        circle_points = np.array([
            center + (np.cos(t) * self.base_0 + np.sin(t) * self.base_1) * self.radius
            for t in self.theta
        ])
        self.circle_color.set_data_3d(circle_points[:, 0], circle_points[:, 1], circle_points[:, 2])

        # 3. Calculate the phase line (the vector rotating inside the cross-sectional circle)
        phase_vector = np.cos(self.phase) * self.base_0 + np.sin(self.phase) * self.base_1
        end_point = center + phase_vector * self.radius

        self.plt_phase.set_data_3d([center[0], end_point[0]],
                                   [center[1], end_point[1]],
                                   [center[2], end_point[2]])

        self.marker_end_1.set_data_3d([end_point[0]], [end_point[1]], [end_point[2]])


def set_radius_color_charge(value):
    global r_color_charge
    r_color_charge = value
    update_diagrams()


def set_radius_rotation_vector(value):
    global r_rotation_vector
    r_rotation_vector = value
    rotation_vector.update_radius(r_rotation_vector)
    update_diagrams()


def set_k(value):
    global k
    k = value
    update_diagrams()


def create_parameter_setter():
    # Controls for the major radius (Rotation Vector)
    frm_r_large = ttk.Labelframe(root, relief='ridge', text="Radius (Large)", labelanchor='n')
    frm_r_large.pack(side='left', padx=5)
    var_r_large = tk.StringVar(root, value=str(r_rotation_vector))
    # Increased the upper limit 'to' from 2.0 to 3.0 to give more room for a larger minor radius
    spn_r_large = tk.Spinbox(
        frm_r_large, textvariable=var_r_large, format='%.1f', from_=0.5, to=3.0, increment=0.1,
        command=lambda: set_radius_rotation_vector(float(var_r_large.get())), width=5
    )
    spn_r_large.pack(side='left', padx=2)

    # Controls for the minor radius (Color Charge)
    frm_r_small = ttk.Labelframe(root, relief='ridge', text="r (Color Charge)", labelanchor='n')
    frm_r_small.pack(side='left', padx=5)
    var_r_small = tk.StringVar(root, value=str(r_color_charge))
    # FIX: Explicitly expanded 'to' to 1.5 so it can easily go beyond 0.3
    spn_r_small = tk.Spinbox(
        frm_r_small, textvariable=var_r_small, format='%.2f', from_=0.05, to=1.5, increment=0.05,
        command=lambda: set_radius_color_charge(float(var_r_small.get())), width=5
    )
    spn_r_small.pack(side='left', padx=2)

    # Controls for the wave number k
    frm_k = ttk.Labelframe(root, relief='ridge', text="k (wave number)", labelanchor='n')
    frm_k.pack(side='left', padx=5)
    var_k = tk.StringVar(root, value=str(k))
    spn_k = tk.Spinbox(
        frm_k, textvariable=var_k, format='%.1f', from_=-10.0, to=10.0, increment=0.5,
        command=lambda: set_k(float(var_k.get())), width=5
    )
    spn_k.pack(side='left', padx=2)


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
    global ring_line
    step = cnt.get()
    omega = 0.1  # Angular velocity for the time evolution of the phase

    # Lists to store the marker coordinates
    marker_x = []
    marker_y = []
    marker_z = []

    for cc in color_charges:
        # Spatial initial phase (k * phi) + temporal phase evolution (step * omega)
        current_phase = (k * cc.phi) + (step * omega)
        cc.update_geometry(r_rotation_vector, r_color_charge, current_phase)

        # Reconstruct the latest end_point coordinates computed inside the ColorCharge instance
        center = np.array([r_rotation_vector * cc.cos_p, r_rotation_vector * cc.sin_p, 0.])
        phase_vector = np.cos(current_phase) * cc.base_0 + np.sin(current_phase) * cc.base_1
        end_point = center + phase_vector * r_color_charge

        marker_x.append(end_point[0])
        marker_y.append(end_point[1])
        marker_z.append(end_point[2])

    # Append the first point to the end to close the ring loop
    marker_x.append(marker_x[0])
    marker_y.append(marker_y[0])
    marker_z.append(marker_z[0])

    # Update the visual line connecting all marker endpoints (Phase Ring)
    if ring_line is None:
        ring_line, = ax0.plot(marker_x, marker_y, marker_z, color="red", linewidth=2, label="Phase Ring")
        ax0.legend(loc='upper right')
    else:
        ring_line.set_data_3d(marker_x, marker_y, marker_z)

    canvas.draw_idle()


def switch():
    global is_play
    is_play = not is_play


def update(f):
    if is_play:
        cnt.count_up()
        update_diagrams()


""" main loop """
if __name__ == '__main__':
    cnt = Counter(ax=ax0, is3d=True, xy=np.array([x_min, y_max]), z=z_max, label="Step=")
    draw_static_diagrams()
    create_animation_controls()
    create_parameter_setter()

    # Create the central major circle reference
    rotation_vector = RotationVector(ax0, r_rotation_vector, "gray")

    # Arrange 48 ColorCharges evenly along the torus circumference in solid red
    color_charges = []
    num_charges = 48

    for i in range(num_charges):
        # Position angle phi on the major circle
        phi = 2.0 * np.pi * i / num_charges

        # Initial phase is set to 0.0 here since it is dynamically controlled in update_diagrams
        cc = ColorCharge(ax0, radius=r_color_charge, phi=phi, phase=0.0, color="darkred")
        color_charges.append(cc)

    update_diagrams()

    anim = animation.FuncAnimation(fig, update, interval=50, save_count=100)
    root.mainloop()