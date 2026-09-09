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
from scipy.spatial.transform import Rotation
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


# ==========================================
# 1. Color Charge Class
# ==========================================
class ColorCharge:
    def __init__(self, ax, origin=np.zeros(3), radius=1.0, color="magenta", ls0="--", ls1="-", lw0=1, lw1=2,
                 is_visible=True, mode=0):
        self.ax = ax
        self.origin = origin
        self.radius = radius
        self.arrow_length = radius
        self.color = color
        self.ls0 = ls0
        self.ls1 = ls1
        self.lw0 = lw0
        self.lw1 = lw1

        self.dif0 = 0.2
        self.phase = 0
        self.is_visible = is_visible
        self.mode = mode

        # --- Local coordinate system bases ---
        self._basis_1 = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_2 = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_3 = np.array([0., 0., 1.])  # Arrow direction

        # --- Phase Circles ---
        self.plt_circle, = self.ax.plot([], [], [], lw=1, ls=self.ls0, color=self.color, alpha=1.)

        # --- Color Charge Waves ---
        self.plt_helix, = self.ax.plot([], [], [], lw=self.lw1, ls=self.ls1, color=self.color, alpha=0.3)
        self.plt_wave0, = self.ax.plot([], [], [], lw=self.lw0, ls=self.ls0, color=self.color, alpha=1.)

        self.plt_wave1, = self.ax.plot([], [], [], lw=self.lw0, ls=self.ls0, color=self.color, alpha=1.)
        self.plt_wave2, = self.ax.plot([], [], [], lw=self.lw0, ls=self.ls0, color=self.color, alpha=1.)
        self.plt_wave3, = self.ax.plot([], [], [], lw=self.lw1, ls=self.ls1, color=self.color, alpha=1.)

        # --- Update diagrams ---
        self.update_diagrams()

    def update_diagrams(self):
        if self.is_visible:
            if self.mode == 0:
                self.plt_helix.set_visible(True)
                self.plt_wave0.set_visible(True)
                self.plt_wave1.set_visible(False)
                self.plt_wave2.set_visible(False)
                self.plt_wave3.set_visible(False)
            else:
                self.plt_helix.set_visible(False)
                self.plt_wave0.set_visible(False)
                self.plt_wave1.set_visible(True)
                self.plt_wave2.set_visible(True)
                self.plt_wave3.set_visible(True)
        else:
            self.plt_helix.set_visible(False)
            self.plt_wave0.set_visible(False)

            self.plt_wave1.set_visible(False)
            self.plt_wave2.set_visible(False)
            self.plt_wave3.set_visible(False)

        # --- Line space ---
        theta = np.linspace(0, 2 * np.pi, 360)

        """
        # --- Update Phase Circle ---
        c_pts = (np.cos(theta)[:, None] * self._basis_1 +
                 np.sin(theta)[:, None] * self._basis_2) * 0 + self.origin
        self.plt_circle.set_data_3d(c_pts[:, 0], c_pts[:, 1], c_pts[:, 2])
        """

        # --- Color Charge Waves ---
        wave_freq = 12
        wave_amp = 0.2

        # -- Helix (electron)
        # 1.Sine wave on radius
        r_wave_helix = self.radius * (1.0 + wave_amp * np.sin(wave_freq * theta - self.phase))

        # 2.Base circle with radius wave
        c_pts_helix = (np.cos(theta)[:, None] * self._basis_1 +
                       np.sin(theta)[:, None] * self._basis_2) * r_wave_helix[:, None] + self.origin

        # 3. Add Cosine wave on _basis_3
        wave_z = wave_amp * np.cos(wave_freq * theta - self.phase)
        c_pts_helix += wave_z[:, None] * self._basis_3

        self.plt_helix.set_data_3d(c_pts_helix[:, 0], c_pts_helix[:, 1], c_pts_helix[:, 2])

        # Additional wave
        c_pts_w0 = (np.cos(theta)[:, None] * self._basis_1 +
                    np.sin(theta)[:, None] * self._basis_2) * r_wave_helix[:, None] + self.origin
        self.plt_wave0.set_data_3d(c_pts_w0[:, 0], c_pts_w0[:, 1], c_pts_w0[:, 2])

        # -- Standing wave (neutrino)
        # wave radius 1
        r_w1 = wave_amp / 2. * np.sin(wave_freq * theta - self.phase)
        r_wave1 = self.radius * (1.0 + r_w1)

        c_pts_w1 = (np.cos(theta)[:, None] * self._basis_1 +
                    np.sin(theta)[:, None] * self._basis_2) * r_wave1[:, None] + self.origin
        self.plt_wave1.set_data_3d(c_pts_w1[:, 0], c_pts_w1[:, 1], c_pts_w1[:, 2])

        # wave radius 2
        r_w2 = wave_amp / 2. * np.sin(wave_freq * theta + self.phase)
        r_wave2 = self.radius * (1.0 + r_w2)

        c_pts_w2 = (np.cos(theta)[:, None] * self._basis_1 +
                    np.sin(theta)[:, None] * self._basis_2) * r_wave2[:, None] + self.origin
        self.plt_wave2.set_data_3d(c_pts_w2[:, 0], c_pts_w2[:, 1], c_pts_w2[:, 2])

        # Standing wave wave1 + wave2
        r_wave3 = self.radius * (1.0 + r_w1 + r_w2)

        c_pts_w3 = (np.cos(theta)[:, None] * self._basis_1 +
                    np.sin(theta)[:, None] * self._basis_2) * r_wave3[:, None] + self.origin
        self.plt_wave3.set_data_3d(c_pts_w3[:, 0], c_pts_w3[:, 1], c_pts_w3[:, 2])

    def apply_rotation(self, angle, axis_vector):
        rot = Rotation.from_rotvec(angle * axis_vector)
        self._basis_1 = rot.apply(self._basis_1)
        self._basis_2 = rot.apply(self._basis_2)
        self._basis_3 = rot.apply(self._basis_3)
        self.update_diagrams()

    def set_origin(self, origin):
        self.origin = origin
        self.update_diagrams()

    def set_mode(self, value):
        self.mode = value
        self.update_diagrams()

    def rotate_phase(self, value):
        self.phase += value
        self.update_diagrams()


# ==========================================
# 2. Rotation Vector Class
# ==========================================
class RotationVector:
    def __init__(self, ax, origin=np.zeros(3), radius=1.0, color="gray", ls0="-", lw0=3, mode=0):
        self.ax = ax
        self.origin = origin
        self.radius = radius
        self.arrow_length = radius
        self.color = color
        self.ls0 = ls0
        self.lw0 = lw0
        self.mode = mode

        if self.mode == 0:
            self.ls = self.ls0
            self.lw = self.lw0
            self.arrow_length = radius

        elif self.mode == 1:
            self.ls = ":"
            self.lw = 1
            self.arrow_length = 0
        else:
            self.ls = self.ls0
            self.lw = self.lw0
            self.arrow_length = radius

        # --- Local coordinate system bases ---
        self._basis_1 = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_2 = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_3 = np.array([0., 0., 1.])  # Arrow direction

        # --- Phase Circles ---
        self.plt_circle, = self.ax.plot([], [], [], lw=self.lw, ls=self.ls, color=self.color, alpha=1.)

        # --- Quiver ---
        self.quiver_arrow = None

        # --- Update diagrams ---
        self.update_diagrams()

    def update_diagrams(self):
        # --- Update Phase Circle ---
        theta = np.linspace(0, 2 * np.pi, 64)

        c_pts = (np.cos(theta)[:, None] * self._basis_1 +
                 np.sin(theta)[:, None] * self._basis_2) * self.radius + self.origin
        self.plt_circle.set_data_3d(c_pts[:, 0], c_pts[:, 1], c_pts[:, 2])

        # --- Update Quiver ---
        if self.quiver_arrow:
            self.quiver_arrow.remove()

        self.quiver_arrow = self.ax.quiver(
            self.origin[0], self.origin[1], self.origin[2],
            self._basis_3[0], self._basis_3[1], self._basis_3[2],
            length=self.arrow_length, color=self.color, linewidth=self.lw,
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

    def set_mode(self, value):
        self.mode = value
        if self.mode == 0:
            self.ls = self.ls0
            self.lw = self.lw0
            self.arrow_length = self.radius
        elif self.mode == 1:
            self.ls = ":"
            self.lw = 1
            self.arrow_length = 0
        else:
            self.ls = self.ls0
            self.lw = self.lw0
            self.arrow_length = self.radius
        self.plt_circle.set_linewidth(self.lw)
        self.plt_circle.set_linestyle(self.ls)

        self.update_diagrams()


# ==========================================
# 3. Rotation Vector Pair Class
# ==========================================

class RotationVectorPair:
    def __init__(self, ax, origin=np.zeros(3), radius=0.5, color0="gray", color1="orange", ls0=":", ls1="--",
                 color_v1="blue", color_v2="gray", ls_v1="-", ls_v2="--", is_visible_c1=True, is_visible_c2=True):
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

        self.is_visible_c1 = is_visible_c1
        self.is_visible_c2 = is_visible_c2

        # --- Local coordinate system bases ---
        self._basis_1 = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_2 = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_3 = np.array([0., 0., 1.])  # Arrow direction

        # --- Guide elements (Circles and Phase line) ---
        self.plt_circle, = self.ax.plot([], [], [], lw=1, ls=self.ls0, color=self.color0, alpha=1.)
        self.plt_phase_line1, = self.ax.plot([], [], [], lw=1, ls=self.ls1, color=self.color1)
        self.plt_phase_line2, = self.ax.plot([], [], [], lw=1, ls=self.ls1, color=self.color1)

        # --- Rotation vectors ---
        self.rotation_vector1 = RotationVector(self.ax, ls0=self.ls_v1, color=self.color_v1)
        self.rotation_vector1.apply_rotation(np.pi / 4, self._basis_1)
        self.rotation_vector1.set_origin(self._basis_1 * self.radius)

        self.rotation_vector2 = RotationVector(self.ax, ls0=self.ls_v2, color=self.color_v2)
        self.rotation_vector2.apply_rotation(- np.pi / 4, self._basis_1)
        self.rotation_vector2.set_origin(- self._basis_1 * self.radius)

        # --- Rotation vectors ---
        self.color_charge1 = ColorCharge(self.ax, is_visible=self.is_visible_c1)
        self.color_charge1.apply_rotation(np.pi / 4, self._basis_1)
        self.color_charge1.set_origin(self._basis_1 * self.radius)

        self.color_charge2 = ColorCharge(self.ax, is_visible=self.is_visible_c2)
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

        self.color_charge1.rotate_phase(angle * 10)
        self.color_charge2.rotate_phase(angle * 10)

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

    def set_mode(self, value):
        self.rotation_vector1.set_mode(value)
        self.rotation_vector2.set_mode(value)

        self.color_charge1.set_mode(value)
        self.color_charge2.set_mode(value)

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
        self.btn_frame.pack(side="left", fill=tk.X, pady=10)
        ttk.Button(self.btn_frame, text="Play / Pause", command=self.toggle_play).pack(side=tk.LEFT, padx=5)

        # Toggle mode (electron:0, neutrino:1)
        self.is_electron = True
        self.btn_frame = ttk.Frame(self.root)
        self.btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(self.btn_frame, text="Electron / Neutrino", command=self.toggle_mode).pack(side=tk.LEFT, padx=5)

        # counter label
        self.counter_var = tk.StringVar(value="Step: 0")
        self.counter_label = ttk.Label(self.btn_frame, textvariable=self.counter_var,)
        self.counter_label.pack(side=tk.RIGHT, padx=20)

        # --- CREATE OBJECTS ---
        # Rotation vector pair
        self.rotation_vector_pair_1 = RotationVectorPair(self.ax0, color_v1="blue", color_v2="lightgray",
                                                         ls_v1="-", ls_v2="--", is_visible_c1=True, is_visible_c2=False)

        self.rotation_vector_pair_2 = RotationVectorPair(self.ax0, color_v1="red", color_v2="green",
                                                         ls_v1="-", ls_v2="-", is_visible_c1=True, is_visible_c2=True)
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

    def toggle_mode(self):
        self.is_electron = not self.is_electron
        if self.is_electron:
            self.rotation_vector_pair_1.set_mode(0)
            self.rotation_vector_pair_2.set_mode(0)
        else:
            self.rotation_vector_pair_1.set_mode(1)
            self.rotation_vector_pair_2.set_mode(1)

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