# ==========================================
# Photon model (none pair model)
# ==========================================

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from scipy.spatial.transform import Rotation
import ctypes
import platform
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Circle


# ==========================================
# 1. RotationVector Class
# ==========================================
class RotationVector:
    def __init__(self, ax, origin=np.zeros(3), radius=1., arrow_length=1.,
                 line_style='-', line_width=1, color='gray',):

        self.ax = ax

        self.origin = origin
        self.radius = radius

        self.arrow_length = arrow_length

        self.line_style = line_style

        self.line_width = line_width
        self.color = color

        # --- Local coordinate system bases ---
        self._basis_x = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_y = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_z = np.array([0., 0., 1.])  # Arrow direction

        # --- Quiver ---
        self.quiver_obj = None

        # --- Guide elements (Circles and Phase line) ---
        # Ensure these are initialized after the bases exist
        self.plt_circle, = self.ax.plot([], [], [], lw=self.line_width, color=self.color, ls=self.line_style,
                                        alpha=1.)

        self.update_diagrams()

    def update_diagrams(self):
        # --- Update Quiver (The Arrow) ---
        if self.quiver_obj:
            self.quiver_obj.remove()

        self.quiver_obj = self.ax.quiver(
             self.origin[0], self.origin[1], self.origin[2],
             self._basis_z[0], self._basis_z[1], self._basis_z[2],
             length=self.arrow_length, color=self.color, linewidth=self.line_width,
             arrow_length_ratio=0.2, normalize=False, ls=self.line_style
        )

        # --- Update Orbital Circle ---
        theta = np.linspace(0, 2 * np.pi, 64)
        # Circle points on the x-y local plane
        c_pts = (np.cos(theta)[:, None] * self._basis_x +
                 np.sin(theta)[:, None] * self._basis_y) * self.radius + self.origin
        self.plt_circle.set_data_3d(c_pts[:, 0], c_pts[:, 1], c_pts[:, 2])

    def apply_rotation(self, angle_rad, axis_vector):
        rot = Rotation.from_rotvec(angle_rad * axis_vector)
        self._basis_x = rot.apply(self._basis_x)
        self._basis_y = rot.apply(self._basis_y)
        self._basis_z = rot.apply(self._basis_z)
        self.update_diagrams()

    def reset(self):
        self._basis_x = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_y = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_z = np.array([0., 0., 1.])  # Arrow direction
        self.update_diagrams()

    def set_origin(self, origin):
        self.origin = origin
        self.update_diagrams()

    def set_radius(self, radius):
        self.radius = radius
        self.update_diagrams()

    def set_arrow_length(self, length):
        self.arrow_length = length
        self.update_diagrams()


# ==========================================
# 2. PrecessionBase Class
# ==========================================
class OrbitBaseTri:
    def __init__(self, ax, origin=np.zeros(3), radius=1., arrow_length=1.732,
                 phase_a=0., phase_b=0., phase_c=0.,
                 line_style='-', line_width=1, color='gray'):

        self.ax = ax

        self.origin = origin
        self.radius = radius

        self.arrow_length = arrow_length

        self.phase_a = phase_a
        self.phase_b = phase_b
        self.phase_c = phase_c

        self.line_style = line_style
        self.line_width = line_width
        self.color = color

        # --- Local coordinate system bases ---
        self._basis_x = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_y = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_z = np.array([0., 0., 1.])  # Arrow direction

        # --- Quiver ---
        self.quiver_obj = None

        # --- Guide elements (Circles and Phase line) ---
        # Ensure these are initialized after the bases exist
        self.plt_circle, = self.ax.plot([], [], [], lw=self.line_width, color=self.color, ls=self.line_style,
                                        alpha=1.)
        self.plt_phase_line_a, = self.ax.plot([], [], [], lw=1., ls="--", color=color)
        self.plt_phase_line_b, = self.ax.plot([], [], [], lw=1., ls="--", color=color)
        self.plt_phase_line_c, = self.ax.plot([], [], [], lw=1., ls="--", color=color)
        self.plt_marker_a, = self.ax.plot([], [], [], marker="o", ms=5, color=color)
        self.plt_marker_b, = self.ax.plot([], [], [], marker="o", ms=5, color=color)
        self.plt_marker_c, = self.ax.plot([], [], [], marker="o", ms=5, color=color)

        self.update_diagrams()

    def update_diagrams(self):
        # --- Update Quiver (The Arrow) ---
        if self.quiver_obj:
            self.quiver_obj.remove()

        self.quiver_obj = self.ax.quiver(
             self.origin[0], self.origin[1], self.origin[2],
             self._basis_z[0], self._basis_z[1], self._basis_z[2],
             length=self.arrow_length, color=self.color, linewidth=self.line_width,
             arrow_length_ratio=0.2, normalize=False, ls=self.line_style
        )

        # --- Update Orbital Circle ---
        theta = np.linspace(0, 2 * np.pi, 64)
        # Circle points on the x-y local plane
        c_pts = (np.cos(theta)[:, None] * self._basis_x +
                 np.sin(theta)[:, None] * self._basis_y) * self.radius + self.origin
        self.plt_circle.set_data_3d(c_pts[:, 0], c_pts[:, 1], c_pts[:, 2])

        # --- Update Phase Marker ---
        p_vec_a = (np.cos(self.phase_a) * self._basis_x +
                   np.sin(self.phase_a) * self._basis_y) * self.radius + self.origin
        self.plt_phase_line_a.set_data_3d([self.origin[0], p_vec_a[0]],
                                          [self.origin[1], p_vec_a[1]],
                                          [self.origin[2], p_vec_a[2]])
        self.plt_marker_a.set_data_3d([p_vec_a[0]], [p_vec_a[1]], [p_vec_a[2]])

        p_vec_b = (np.cos(self.phase_b) * self._basis_x +
                   np.sin(self.phase_b) * self._basis_y) * self.radius + self.origin
        self.plt_phase_line_b.set_data_3d([self.origin[0], p_vec_b[0]],
                                          [self.origin[1], p_vec_b[1]],
                                          [self.origin[2], p_vec_b[2]])
        self.plt_marker_b.set_data_3d([p_vec_b[0]], [p_vec_b[1]], [p_vec_b[2]])

        p_vec_c = (np.cos(self.phase_c) * self._basis_x +
                   np.sin(self.phase_c) * self._basis_y) * self.radius + self.origin
        self.plt_phase_line_c.set_data_3d([self.origin[0], p_vec_c[0]],
                                          [self.origin[1], p_vec_c[1]],
                                          [self.origin[2], p_vec_c[2]])
        self.plt_marker_c.set_data_3d([p_vec_c[0]], [p_vec_c[1]], [p_vec_c[2]])

    def apply_rotation(self, angle_rad, axis_vector):
        rot = Rotation.from_rotvec(angle_rad * axis_vector)
        self._basis_x = rot.apply(self._basis_x)
        self._basis_y = rot.apply(self._basis_y)
        self._basis_z = rot.apply(self._basis_z)
        self.update_diagrams()

    def rotate_phase_a(self, angle_rad):
        self.phase_a = (self.phase_a + angle_rad) % (2 * np.pi)
        self.update_diagrams()

    def rotate_phase_b(self, angle_rad):
        self.phase_b = (self.phase_b + angle_rad) % (2 * np.pi)
        self.update_diagrams()

    def rotate_phase_c(self, angle_rad):
        self.phase_c = (self.phase_c + angle_rad) % (2 * np.pi)
        self.update_diagrams()

    def set_phase_a(self, angle_rad):
        self.phase_a = angle_rad
        self.update_diagrams()

    def set_phase_b(self, angle_rad):
        self.phase_b = angle_rad
        self.update_diagrams()

    def set_phase_c(self, angle_rad):
        self.phase_c = angle_rad
        self.update_diagrams()

    def reset(self):
        self.phase_a = 0.
        self.phase_b = 0.
        self.phase_c = 0.
        self._basis_x = np.array([1., 0., 0.])  # Orbital plane base 1
        self._basis_y = np.array([0., 1., 0.])  # Orbital plane base 2
        self._basis_z = np.array([0., 0., 1.])  # Arrow direction
        self.update_diagrams()

    def set_origin(self, origin):
        self.origin = origin
        self.update_diagrams()

    def set_radius(self, radius):
        self.radius = radius
        self.update_diagrams()

    def set_arrow_length(self, length):
        self.arrow_length = length
        self.update_diagrams()

    def get_phase_point_a(self):
        p_vec_a = (np.cos(self.phase_a) * self._basis_x +
                   np.sin(self.phase_a) * self._basis_y) * self.radius + self.origin
        return p_vec_a

    def get_phase_point_b(self):
        p_vec_b = (np.cos(self.phase_b) * self._basis_x +
                   np.sin(self.phase_b) * self._basis_y) * self.radius + self.origin
        return p_vec_b

    def get_phase_point_c(self):
        p_vec_c = (np.cos(self.phase_c) * self._basis_x +
                   np.sin(self.phase_c) * self._basis_y) * self.radius + self.origin
        return p_vec_c


# ==========================================
# 3. App
# ==========================================
class PhotonApp:
    def __init__(self, root):
        self.title = "Photon model (rotation vector none pair model)"
        self.root = root
        self.root.title(self.title)

        # --- COUNTER VARIABLE ---
        self.frame_count = 0

        # --- HIGH DPI SUPPORT FOR WINDOWS ---
        if platform.system() == "Windows":
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass

        # --- STYLE & FONTS ---
        style = ttk.Style()
        style.configure("BigFont.TButton", font=("", 24, ""))
        style.configure("Counter.TLabel", font=("Consolas", 24, "bold"), foreground="blue")
        style.configure("BigFont.TLabel", font=("", 24, ""))

        # --- PLOT SETUP ---
        self.fig = Figure(figsize=(8, 8), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- ADDING THE TOOLBAR ---
        self.toolbar_frame = ttk.Frame(self.root)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

        # --- MATPLOTLIB FIGURE SETUP ---
        self.ax.set_box_aspect((1, 1, 1))
        lim = 2.5
        self.ax.set_xlim(-lim, lim)
        self.ax.set_ylim(-lim, lim)
        self.ax.set_zlim(-lim, lim)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.ax.set_title(self.title, fontsize=30)

        # --- CREATE STATIC DIAGRAMS - CENTER LINES ---
        line_axis_x = art3d.Line3D([-lim, lim], [0., 0.], [0., 0.], color="gray", ls="-.", linewidth=1)
        self.ax.add_line(line_axis_x)
        line_axis_y = art3d.Line3D([0., 0.], [-lim, lim], [0., 0.], color="gray", ls="-.", linewidth=1)
        self.ax.add_line(line_axis_y)
        line_axis_z = art3d.Line3D([0., 0.], [0., 0.], [-lim, lim], color="gray", ls="-.", linewidth=1)
        self.ax.add_line(line_axis_z)

        # --- CREATE STATIC DIAGRAMS - ADDITIONAL CIRCLES ---
        """
        c00 = Circle((0, 0), np.sqrt(2)/2, ec='gray', ls=":", fill=False)
        self.ax.add_patch(c00)
        art3d.pathpatch_2d_to_3d(c00, z=0, zdir="x")
        c01 = Circle((0, 0), np.sqrt(2)/2, ec='gray', ls=":", fill=False)
        self.ax.add_patch(c01)
        art3d.pathpatch_2d_to_3d(c01, z=0, zdir="y")
        c02 = Circle((0, 0), np.sqrt(2)/2, ec='gray', ls=":", fill=False)
        self.ax.add_patch(c02)
        art3d.pathpatch_2d_to_3d(c02, z=0, zdir="z")
        """

        # --- PARAMETERS ---
        self.orbit_radius_init = 0.2
        self.phase_a_deg = 0.
        self.phase_b_deg = 120.
        self.phase_c_deg = 240.

        # --- SET ROTATION VELOCITY ---
        self.velocity_base = -0.05                 # Base velocity
        self.delta_phase = self.velocity_base

        # --- CREATE ORBIT BASE ---
        self.orbit_base0 = OrbitBaseTri(self.ax, radius=self.orbit_radius_init)
        self.orbit_base0.apply_rotation((np.pi/4.), np.array([1., 0., 0.]))
        self.orbit_base0.apply_rotation(0.615, np.array([0., 0., 1.]))

        self.orbit_base0.set_phase_a(np.deg2rad(self.phase_a_deg))
        self.orbit_base0.set_phase_b(np.deg2rad(self.phase_b_deg))
        self.orbit_base0.set_phase_c(np.deg2rad(self.phase_c_deg))

        # --- CREATE ROTATION VECTORS ---
        self.rotation_vector_red = RotationVector(self.ax, color='red', line_width=3)
        self.rotation_vector_red.apply_rotation((np.pi / 2.), np.array([0., 1., 0.]))

        self.rotation_vector_green = RotationVector(self.ax, color='green', line_width=3)
        self.rotation_vector_green.apply_rotation((np.pi / 2.), np.array([1., 0., 0.]))

        self.rotation_vector_blue = RotationVector(self.ax, color='blue', line_width=3)

        # --- UPDATE LOCATION OF ORBIT_BASES & ROTATION_VECTORS ---
        self.update_orbit_location()

        # --- CREATE PHASE TRACE ---

        # --- UI - BUTTONS ---
        self.btn_frame = ttk.Frame(self.root)
        self.btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        ttk.Button(self.btn_frame, text="Play / Pause", style="BigFont.TButton",
                   command=self.toggle_play).pack(side=tk.LEFT, padx=5)

        ttk.Button(self.btn_frame, text="Reset", style="BigFont.TButton",
                   command=self.reset).pack(side=tk.LEFT, padx=5)

        # --- UI SPINBOX ---
        label_orbit_r = ttk.Label(self.btn_frame, text="Orbit Radius", style="BigFont.TLabel")
        label_orbit_r.pack(side='left')
        var_orbit_r = tk.StringVar(self.btn_frame)
        var_orbit_r.set(str(self.orbit_radius_init))

        sb_orbit_r = tk.Spinbox(
            self.btn_frame, textvariable=var_orbit_r, format="%.2f", from_=0.01, to=1., increment=0.01,
            command=lambda: self.set_orbit_radius(float(var_orbit_r.get())), width=5, font=("Arial", 24)
        )
        sb_orbit_r.pack(side='left')

        label_phase_a = ttk.Label(self.btn_frame, text="Phase_a", style="BigFont.TLabel")
        label_phase_a.pack(side='left')
        var_phase_a = tk.StringVar(self.btn_frame)
        var_phase_a.set(str(self.phase_a_deg))

        sb_phase_a = tk.Spinbox(
            self.btn_frame, textvariable=var_phase_a, format="%.1f", from_=-360., to=360., increment=1.,
            command=lambda: self.set_phase_a(float(var_phase_a.get())), width=6, font=("Arial", 24)
        )
        sb_phase_a.pack(side='left')

        label_phase_b = ttk.Label(self.btn_frame, text="Phase_b", style="BigFont.TLabel")
        label_phase_b.pack(side='left')
        var_phase_b = tk.StringVar(self.btn_frame)
        var_phase_b.set(str(self.phase_b_deg))

        sb_phase_b = tk.Spinbox(
            self.btn_frame, textvariable=var_phase_b, format="%.1f", from_=-360., to=360., increment=1.,
            command=lambda: self.set_phase_b(float(var_phase_b.get())), width=6, font=("Arial", 24)
        )
        sb_phase_b.pack(side='left')

        label_phase_c = ttk.Label(self.btn_frame, text="Phase_c", style="BigFont.TLabel")
        label_phase_c.pack(side='left')
        var_phase_c = tk.StringVar(self.btn_frame)
        var_phase_c.set(str(self.phase_c_deg))

        sb_phase_c = tk.Spinbox(
            self.btn_frame, textvariable=var_phase_c, format="%.1f", from_=-360., to=360., increment=1.,
            command=lambda: self.set_phase_c(float(var_phase_c.get())), width=6, font=("Arial", 24)
        )
        sb_phase_c.pack(side='left')

        # --- UI - COUNTER LABEL ---
        self.counter_var = tk.StringVar(value="Step: 0")
        self.counter_label = ttk.Label(self.btn_frame, textvariable=self.counter_var, style="Counter.TLabel")
        self.counter_label.pack(side=tk.RIGHT, padx=20)

        # --- ANIMATION CONTROL ---
        self.is_playing = False
        self.anim = animation.FuncAnimation(self.fig, self.loop, interval=40, cache_frame_data=False)

    def set_phase_a(self, phase_deg):
        self.phase_a_deg = phase_deg
        self.orbit_base0.set_phase_a(np.deg2rad(self.phase_a_deg))
        self.update_orbit_location()

    def set_phase_b(self, phase_deg):
        self.phase_b_deg = phase_deg
        self.orbit_base0.set_phase_a(np.deg2rad(self.phase_b_deg))
        self.update_orbit_location()

    def set_phase_c(self, phase_deg):
        self.phase_c_deg = phase_deg
        self.orbit_base0.set_phase_a(np.deg2rad(self.phase_c_deg))
        self.update_orbit_location()

    def set_orbit_radius(self, radius):
        self.orbit_base0.set_radius(radius)
        self.update_orbit_location()

    def reset(self):
        self.is_playing = False
        self.canvas.draw_idle()

    def toggle_play(self):
        self.is_playing = not self.is_playing

    def update_orbit_location(self):
        orbit_point_a = self.orbit_base0.get_phase_point_a()
        orbit_point_b = self.orbit_base0.get_phase_point_b()
        orbit_point_c = self.orbit_base0.get_phase_point_c()

        self.rotation_vector_red.set_origin(orbit_point_a)
        self.rotation_vector_green.set_origin(orbit_point_b)
        self.rotation_vector_blue.set_origin(orbit_point_c)

    def update_diagrams_with_phase(self, phase):
        self.orbit_base0.set_phase_a(phase + np.deg2rad(self.phase_a_deg))
        self.orbit_base0.set_phase_b(phase + np.deg2rad(self.phase_b_deg))
        self.orbit_base0.set_phase_c(phase + np.deg2rad(self.phase_c_deg))

        self.update_orbit_location()

    def loop(self, frame):
        if self.is_playing:
            # --- INCREMENT COUNTER ---
            self.frame_count += 1
            self.counter_var.set(f"Step: {self.frame_count}")

            # --- UPDATE DIAGRAMS ---
            phase = - np.pi * self.frame_count / 180. * 4

            self.update_diagrams_with_phase(phase)

            # --- UPDATE TRACE ---
            pass

            self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotonApp(root)
    root.mainloop()