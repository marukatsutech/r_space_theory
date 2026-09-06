# ==========================================
# Lepton model with Hopf link rotation vector pairs
# ==========================================

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.spatial.transform import Rotation
from collections import deque
import ctypes
import platform
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Circle


# ==========================================
# 1. Color Charge Class
# ==========================================
class ColorCharge:
    def __init__(self, ax, origin=np.zeros(3), radius=1.2, color="magenta", ls0="--", ls1="-", lw0=1, lw1=2):
        self.ax = ax
        self.origin = origin
        self.radius = radius
        self.arrow_length = radius
        self.color = color
        self.ls0 = ls0
        self.ls1 = ls1
        self.lw0 = lw0
        self.lw1 = lw1

        # --- Local coordinate system bases ---
        self._basis_1 = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_2 = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_3 = np.array([0., 0., 1.])  # Arrow direction

        # --- Phase Circles ---
        self.plt_circle, = self.ax.plot([], [], [], lw=1, ls=self.ls0, color=self.color, alpha=1.)

        # --- Waves ---
        self.plt_wave1, = self.ax.plot([], [], [], lw=self.lw0, ls=self.ls0, color=self.color, alpha=1.)
        self.plt_wave2, = self.ax.plot([], [], [], lw=self.lw0, ls=self.ls0, color=self.color, alpha=1.)
        self.plt_wave3, = self.ax.plot([], [], [], lw=self.lw1, ls=self.ls1, color=self.color, alpha=1.)

        # --- Update diagrams ---
        self.update_diagrams()

    def update_diagrams(self):
        # --- Update Phase Circle ---
        theta = np.linspace(0, 2 * np.pi, 64)

        c_pts = (np.cos(theta)[:, None] * self._basis_1 +
                 np.sin(theta)[:, None] * self._basis_2) * self.radius + self.origin
        self.plt_circle.set_data_3d(c_pts[:, 0], c_pts[:, 1], c_pts[:, 2])

    def apply_rotation(self, angle, axis_vector):
        rot = Rotation.from_rotvec(angle * axis_vector)
        self._basis_1 = rot.apply(self._basis_1)
        self._basis_2 = rot.apply(self._basis_2)
        self._basis_3 = rot.apply(self._basis_3)
        self.update_diagrams()

    def set_origin(self, origin):
        self.origin = origin
        self.update_diagrams()


# ==========================================
# 2. Rotation Vector Class
# ==========================================
class RotationVector:
    def __init__(self, ax, origin=np.zeros(3), radius=1.0, color="gray", ls="-"):
        self.ax = ax
        self.origin = origin
        self.radius = radius
        self.arrow_length = radius
        self.color = color
        self.ls = ls

        # --- Local coordinate system bases ---
        self._basis_1 = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_2 = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_3 = np.array([0., 0., 1.])  # Arrow direction

        # --- Phase Circles ---
        self.plt_circle, = self.ax.plot([], [], [], lw=1, ls=self.ls, color=self.color, alpha=1.)

        # --- Quiver ---
        self.quiver_obj_base = None

        # --- Update diagrams ---
        self.update_diagrams()

    def update_diagrams(self):
        # --- Update Phase Circle ---
        theta = np.linspace(0, 2 * np.pi, 64)

        c_pts = (np.cos(theta)[:, None] * self._basis_1 +
                 np.sin(theta)[:, None] * self._basis_2) * self.radius + self.origin
        self.plt_circle.set_data_3d(c_pts[:, 0], c_pts[:, 1], c_pts[:, 2])

        # --- Update Quiver ---
        if self.quiver_obj_base:
            self.quiver_obj_base.remove()

        self.quiver_obj_base = self.ax.quiver(
            self.origin[0], self.origin[1], self.origin[2],
            self._basis_3[0], self._basis_3[1], self._basis_3[2],
            length=self.arrow_length, color=self.color, linewidth=3,
            arrow_length_ratio=0.2, normalize=True, ls=self.ls
        )

    def apply_rotation(self, angle, axis_vector):
        rot = Rotation.from_rotvec(angle * axis_vector)
        self._basis_1 = rot.apply(self._basis_1)
        self._basis_2 = rot.apply(self._basis_2)
        self._basis_3 = rot.apply(self._basis_3)
        self.update_diagrams()

    def set_origin(self, origin):
        self.origin = origin
        self.update_diagrams()


# ==========================================
# 3. Rotation Vector Pair Class
# ==========================================

class RotationVectorPair:
    def __init__(self, ax, origin=np.zeros(3), radius=0.5, color0="gray", color1="orange", ls0=":", ls1="--",
                 color_v1="blue", color_v2="gray", ls_v1="-", ls_v2="--"):
        self.ax = ax
        self.origin = origin
        self.radius = radius
        self.color0 = color0
        self.color1 = color1
        self.ls0 = ls0
        self.ls1 = ls1

        self.color_v1 = color_v1
        self.color_v2 = color_v2
        self.ls_v1 = ls_v1
        self.ls_v2 = ls_v2

        self.phase = 0.

        # --- Local coordinate system bases ---
        self._basis_1 = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_2 = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_3 = np.array([0., 0., 1.])  # Arrow direction

        # --- Guide elements (Circles and Phase line) ---
        self.plt_circle, = self.ax.plot([], [], [], lw=1, ls=self.ls0, color=self.color0, alpha=1.)
        self.plt_phase_line1, = self.ax.plot([], [], [], lw=1, ls=self.ls1, color=self.color1)
        self.plt_phase_line2, = self.ax.plot([], [], [], lw=1, ls=self.ls1, color=self.color1)

        # --- Rotation vectors ---
        self.rotation_vector1 = RotationVector(self.ax, ls=self.ls_v1, color=self.color_v1)
        self.rotation_vector1.apply_rotation(np.pi / 4, self._basis_1)
        self.rotation_vector1.set_origin(self._basis_1 * self.radius)

        self.rotation_vector2 = RotationVector(self.ax, ls=self.ls_v2, color=self.color_v2)
        self.rotation_vector2.apply_rotation(- np.pi / 4, self._basis_1)
        self.rotation_vector2.set_origin(- self._basis_1 * self.radius)

        # --- Rotation vectors ---
        self.color_charge1 = ColorCharge(self.ax)
        self.color_charge1.apply_rotation(np.pi / 4, self._basis_1)
        self.color_charge1.set_origin(self._basis_1 * self.radius)

        self.color_charge2 = ColorCharge(self.ax)
        self.color_charge2.apply_rotation(- np.pi / 4, self._basis_1)
        self.color_charge2.set_origin(- self._basis_1 * self.radius)

        # --- Update diagrams ---
        self.update_diagrams()

    def update_diagrams(self):
        # --- Update Orbital Circle ---
        theta = np.linspace(0, 2 * np.pi, 64)

        c_pts = (np.cos(theta)[:, None] * self._basis_1 +
                 np.sin(theta)[:, None] * self._basis_2) * self.radius + self.origin
        self.plt_circle.set_data_3d(c_pts[:, 0], c_pts[:, 1], c_pts[:, 2])

        # --- Phase lines ---
        p_vec1 = (np.cos(self.phase) * self._basis_1 +
                  np.sin(self.phase) * self._basis_2) * self.radius + self.origin
        self.plt_phase_line1.set_data_3d([self.origin[0], p_vec1[0]],
                                         [self.origin[1], p_vec1[1]],
                                         [self.origin[2], p_vec1[2]])

        p_vec2 = (np.cos(self.phase) * - self._basis_1 +
                  np.sin(self.phase) * - self._basis_2) * self.radius + self.origin
        self.plt_phase_line2.set_data_3d([self.origin[0], p_vec2[0]],
                                         [self.origin[1], p_vec2[1]],
                                         [self.origin[2], p_vec2[2]])

        # Rotation Vectors
        self.rotation_vector1.set_origin(np.array([p_vec1[0], p_vec1[1], p_vec1[2]]))
        self.rotation_vector2.set_origin(np.array([p_vec2[0], p_vec2[1], p_vec2[2]]))

        # Color Charges
        self.color_charge1.set_origin(np.array([p_vec1[0], p_vec1[1], p_vec1[2]]))
        self.color_charge2.set_origin(np.array([p_vec2[0], p_vec2[1], p_vec2[2]]))

    def apply_rotation(self, angle, axis_vector):
        rot = Rotation.from_rotvec(angle * axis_vector)
        self._basis_1 = rot.apply(self._basis_1)
        self._basis_2 = rot.apply(self._basis_2)
        self._basis_3 = rot.apply(self._basis_3)

        self.rotation_vector1.apply_rotation(angle, axis_vector)
        self.rotation_vector2.apply_rotation(angle, axis_vector)

        self.color_charge1.apply_rotation(angle, axis_vector)
        self.color_charge2.apply_rotation(angle, axis_vector)

        self.update_diagrams()

    def rotate_phase(self, angle):
        self.phase = self.phase + angle

        self.rotation_vector1.apply_rotation(angle, self._basis_3)
        self.rotation_vector2.apply_rotation(angle, self._basis_3)

        self.color_charge1.apply_rotation(angle, self._basis_3)
        self.color_charge2.apply_rotation(angle, self._basis_3)

        self.update_diagrams()

    def reset(self):
        self.phase = 0.
        self._basis_1 = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_2 = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_3 = np.array([0., 0., 1.])  # Arrow direction
        self.update_diagrams()

    def set_origin(self, origin):
        self.origin = origin
        self.update_diagrams()

    def get_phase_point_1(self):
        p_vec = (np.cos(self.phase) * self._basis_1 +
                 np.sin(self.phase) * self._basis_2) * self.radius + self.origin
        return p_vec

    def get_phase_point_2(self):
        p_vec = (np.cos(self.phase) * self._basis_1 +
                 np.sin(self.phase) * self._basis_2) * - self.radius + self.origin
        return p_vec


# ==========================================
# 3. App
# ==========================================
class LeptonApp:
    def __init__(self, root):
        # --- TK INTER SETUP ---
        self.title = "Lepton model (with color charge)"
        self.root = root
        self.root.title(self.title)

        # Plot setup
        self.fig = Figure()
        self.ax0 = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Adding toolbar
        self.toolbar_frame = ttk.Frame(self.root)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

        # User interface
        pass

        # --- MATPLOTLIB FIGURE SETUP ---
        self.ax0.set_box_aspect((1, 1, 1))
        lim = 2.0
        self.ax0.set_xlim(-lim, lim)
        self.ax0.set_ylim(-lim, lim)
        self.ax0.set_zlim(-lim, lim)
        self.ax0.set_xlabel("X")
        self.ax0.set_ylabel("Y")
        self.ax0.set_zlabel("Z")
        self.ax0.set_title(self.title)

        # --- ANIMATION CONTROL ---
        self.is_playing = False
        self.anim = animation.FuncAnimation(self.fig, self.loop, interval=40, cache_frame_data=False)
        self.frame_count = 0

        # Toggle animation
        self.btn_frame = ttk.Frame(self.root)
        self.btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        ttk.Button(self.btn_frame, text="Play / Pause", command=self.toggle_play).pack(side=tk.LEFT, padx=5)

        # counter label
        self.counter_var = tk.StringVar(value="Step: 0")
        self.counter_label = ttk.Label(self.btn_frame, textvariable=self.counter_var,)
        self.counter_label.pack(side=tk.RIGHT, padx=20)

        # --- CREATE OBJECTS ---
        # Rotation vector pair
        self.rotation_vector_pair_1 = RotationVectorPair(self.ax0, color_v1="blue", color_v2="lightgray",
                                                         ls_v1="-", ls_v2="--")

        self.rotation_vector_pair_2 = RotationVectorPair(self.ax0, color_v1="red", color_v2="green",
                                                         ls_v1="-", ls_v2="-")
        self.rotation_vector_pair_2.apply_rotation(- np.pi / 4, np.array([1., 0., 0.]))
        origin = self.rotation_vector_pair_1.get_phase_point_2()
        self.rotation_vector_pair_2.set_origin(origin)

        # Draw center lines
        line_axis_x = art3d.Line3D([-lim, lim], [0., 0.], [0., 0.], color="gray", ls="-.", linewidth=1)
        self.ax0.add_line(line_axis_x)
        line_axis_y = art3d.Line3D([0., 0.], [-lim, lim], [0., 0.], color="gray", ls="-.", linewidth=1)
        self.ax0.add_line(line_axis_y)
        line_axis_z = art3d.Line3D([0., 0.], [0., 0.], [-lim, lim], color="gray", ls="-.", linewidth=1)
        self.ax0.add_line(line_axis_z)

    def toggle_play(self):
        self.is_playing = not self.is_playing

    def update_diagrams(self):
        pass

    def loop(self, frame):
        if self.is_playing:
            self.frame_count += 1
            self.counter_var.set(f"Step: {self.frame_count}")
            v_base = - 0.05

            self.rotation_vector_pair_1.rotate_phase(v_base)

            self.rotation_vector_pair_2.apply_rotation(v_base, np.array([0., 0., 1.]))
            origin = self.rotation_vector_pair_1.get_phase_point_2()
            self.rotation_vector_pair_2.set_origin(origin)
            self.rotation_vector_pair_2.rotate_phase(v_base)

            self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    app = LeptonApp(root)
    root.mainloop()