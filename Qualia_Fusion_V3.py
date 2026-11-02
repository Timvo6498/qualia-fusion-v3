"""
Qualia Fusion V3 - Grunge / Cyberpunk Edition
Fuses Real_TimeVisualizer (particles + attractor + trails) + Gemini_Visualizer2 (radial waves + UX telemetry)
For the C64-at-4, Mellon-Collie-at-15 kid.

Run: python Qualia_Fusion_V3.py
Requires: python3 + tkinter (built-in)
"""

import math
import random
import time
import json
import tkinter as tk
from tkinter import ttk


class QualiaFusionV3:
    def __init__(self, root):
        self.root = root
        self._running = True
        self.root.title("Qualia Fusion V3 // Mellon Collie Engine [C64 MODE]")
        self.root.geometry("1280x750")
        self.root.configure(bg="#0b0b13")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Params - your original manuscript vars + new
        self.ea_var = tk.DoubleVar(value=8.0)
        self.pc_var = tk.DoubleVar(value=11.0)
        self.o2_var = tk.DoubleVar(value=10.0)  # trail / num lines
        self.qa_var = tk.DoubleVar(value=14.0)
        self.freq_var = tk.DoubleVar(value=3.5)
        self.speed_var = tk.DoubleVar(value=1.2)

        self.is_rotating = tk.BooleanVar(value=True)
        self.show_particles = tk.BooleanVar(value=True)
        self.show_waves = tk.BooleanVar(value=True)
        self.glow_mode = tk.BooleanVar(value=True)

        # Particles
        self.num_particles = 140
        self.particles = []
        self.rotation_angle = 0.0
        self.time_step = 0.0

        # Telemetry (from v2)
        self.session_start = time.time()
        self.task_start = time.time()
        self.interaction_count = 0
        self.event_log = []
        self.current_task = 0
        self.tasks = [
            {"id": 1, "desc": "Task 1: EA 15 + QA 18 + Glow ON -> Find chaos"},
            {"id": 2, "desc": "Task 2: Pause, PC 5, Waves only -> Find calm"},
        ]

        self._build_ui()
        self.root.update_idletasks()
        self._init_particles()
        self.animate()

    def _on_close(self):
        self._running = False
        self.root.destroy()

    def _build_ui(self):
        # LEFT PANEL
        panel = tk.Frame(self.root, bg="#15151f", width=320)
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        panel.pack_propagate(False)

        tk.Label(panel, text="QUALIA FUSION V3", fg="#00e5ff", bg="#15151f",
                 font=("Courier", 13, "bold")).pack(anchor="w", pady=(0, 2))
        tk.Label(panel, text="C64 @4 // Mellon Collie @15 // Hackers @15", fg="#66667a", bg="#15151f",
                 font=("Courier", 7)).pack(anchor="w", pady=(0, 12))

        # Task frame
        task_frame = tk.LabelFrame(panel, text="UX Research Prompt", fg="#00e5ff", bg="#23232f",
                                   font=("Arial", 9, "bold"), padx=8, pady=8)
        task_frame.pack(fill=tk.X, pady=(0, 10))

        self.task_label = tk.Label(task_frame, text=self.tasks[0]["desc"], fg="#e0e0ff", bg="#23232f",
                                   wraplength=270, justify=tk.LEFT, font=("Arial", 9))
        self.task_label.pack(anchor="w")

        tk.Button(task_frame, text="Complete Task & Next", bg="#00e5ff", fg="#000", font=("Arial", 8, "bold"),
                  command=self.complete_task).pack(fill=tk.X, pady=(8, 0))

        # Toggles
        togg_frame = tk.Frame(panel, bg="#15151f")
        togg_frame.pack(fill=tk.X, pady=6)
        for txt, var in [("Rotate", self.is_rotating), ("Particles", self.show_particles),
                         ("Waves", self.show_waves), ("GLOW", self.glow_mode)]:
            cb = tk.Checkbutton(togg_frame, text=txt, variable=var, fg="#aaaacc", bg="#15151f",
                                selectcolor="#15151f", activebackground="#15151f",
                                font=("Arial", 8), command=lambda n=txt: self._log_event("toggle", n, var.get()))
            cb.pack(side=tk.LEFT, padx=4)

        # Sliders
        self._slider(panel, "Energy Awareness (EA) - Speed", self.ea_var, 1, 20)
        self._slider(panel, "Perception Constant (PC) - Gravity", self.pc_var, 1, 25)
        self._slider(panel, "Infinity Scale (O2) - Trail/Count", self.o2_var, 1, 20)
        self._slider(panel, "Qualia Amplitude (QA) - Chaos", self.qa_var, 1, 30)
        self._slider(panel, "Harmonic Frequency", self.freq_var, 0.5, 10)
        self._slider(panel, "Rotation Speed", self.speed_var, 0.1, 5)

        # Metrics
        metrics = tk.LabelFrame(panel, text="Live Telemetry (C64 style)", fg="#ffab00", bg="#15151f",
                                font=("Courier", 9, "bold"), padx=8, pady=8)
        metrics.pack(fill=tk.X, pady=(12, 0))
        self.clicks_lbl = tk.Label(metrics, text="Interactions: 0", fg="#cccccc", bg="#15151f", font=("Courier", 8))
        self.clicks_lbl.pack(anchor="w")
        self.timer_lbl = tk.Label(metrics, text="Task: 0.0s | Session: 0.0s", fg="#cccccc", bg="#15151f", font=("Courier", 8))
        self.timer_lbl.pack(anchor="w")
        self.fps_lbl = tk.Label(metrics, text="FPS: --", fg="#00e5ff", bg="#15151f", font=("Courier", 8, "bold"))
        self.fps_lbl.pack(anchor="w")

        btns = tk.Frame(panel, bg="#15151f")
        btns.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        tk.Button(btns, text="Re-seed Field [R]", bg="#00e5ff", fg="#000", font=("Arial", 9, "bold"),
                  command=self._init_particles).pack(fill=tk.X, pady=2)
        tk.Button(btns, text="Export JSON", bg="#2e7d32", fg="#fff", font=("Arial", 9, "bold"),
                  command=self.export_data).pack(fill=tk.X, pady=2)
        tk.Button(btns, text="Mellon Collie Preset", bg="#4a1a6b", fg="#fff", font=("Arial", 8),
                  command=self.load_mellon_preset).pack(fill=tk.X, pady=2)

        # CANVAS
        self.canvas = tk.Canvas(self.root, bg="#05050a", highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.root.bind("<r>", lambda e: self._init_particles())
        self.root.bind("<R>", lambda e: self._init_particles())
        self.root.bind("<space>", lambda e: self.is_rotating.set(not self.is_rotating.get()))

        # FPS tracking
        self._last_fps_time = time.time()
        self._frame_count = 0

    def _slider(self, parent, label_text, variable, from_, to_):
        f = tk.Frame(parent, bg="#15151f")
        f.pack(fill=tk.X, pady=4)
        hdr = tk.Frame(f, bg="#15151f")
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=label_text, fg="#8a8a9a", bg="#15151f", font=("Arial", 8)).pack(side=tk.LEFT)
        tk.Label(hdr, textvariable=variable, fg="#00e5ff", bg="#15151f", font=("Courier", 8, "bold")).pack(side=tk.RIGHT)
        scale = ttk.Scale(f, from_=from_, to=to_, variable=variable, orient=tk.HORIZONTAL,
                          command=lambda v, name=label_text: self.on_slider_move(name, variable.get()))
        scale.pack(fill=tk.X)

    def _log_event(self, typ, control, value):
        self.interaction_count += 1
        self.clicks_lbl.config(text=f"Interactions: {self.interaction_count}")
        self.event_log.append({
            "t": round(time.time() - self.session_start, 3),
            "type": typ,
            "control": control,
            "value": round(float(value), 3) if isinstance(value, (int, float)) else str(value),
            "task_id": self.tasks[self.current_task]["id"] if self.current_task < len(self.tasks) else 0
        })

    def on_slider_move(self, name, value):
        self._log_event("slider", name, value)
        # don't redraw here - animate loop handles it

    def _init_particles(self):
        w = self.canvas.winfo_width() or 900
        h = self.canvas.winfo_height() or 600
        cx, cy = w / 2, h / 2
        self.particles = []
        for _ in range(self.num_particles):
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(30, min(w, h) * 0.42)
            self.particles.append({
                "x": cx + dist * math.cos(ang),
                "y": cy + dist * math.sin(ang),
                "vx": random.uniform(-1.2, 1.2),
                "vy": random.uniform(-1.2, 1.2),
                "history": [],
                "hue_offset": random.randint(0, 60)
            })
        self._log_event("button", "Re-seed", 1)

    def complete_task(self):
        elapsed = round(time.time() - self.task_start, 2)
        self.event_log.append({
            "t": round(time.time() - self.session_start, 3),
            "type": "task_complete",
            "task_id": self.tasks[self.current_task]["id"],
            "elapsed": elapsed
        })
        if self.current_task + 1 < len(self.tasks):
            self.current_task += 1
            self.task_label.config(text=self.tasks[self.current_task]["desc"])
            self.task_start = time.time()
        else:
            self.task_label.config(text="All done! Export your data. You did it like in '95.")

    def export_data(self):
        data = {
            "meta": "Qualia Fusion V3 - from C64 kid",
            "session_duration": round(time.time() - self.session_start, 2),
            "total_interactions": self.interaction_count,
            "final_params": {
                "EA": self.ea_var.get(), "PC": self.pc_var.get(),
                "O2": self.o2_var.get(), "QA": self.qa_var.get(),
                "freq": self.freq_var.get(), "speed": self.speed_var.get()
            },
            "log": self.event_log
        }
        fname = f"qualia_fusion_{int(time.time())}.json"
        with open(fname, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[EXPORTED] {fname}")

    def load_mellon_preset(self):
        # dreamy, sad, infinite
        self.ea_var.set(6.0)
        self.pc_var.set(14.0)
        self.o2_var.set(16.0)
        self.qa_var.set(22.0)
        self.freq_var.set(2.2)
        self.speed_var.set(0.6)
        self.show_particles.set(True)
        self.show_waves.set(True)
        self.glow_mode.set(True)
        self._log_event("preset", "Mellon Collie", 1)

    def animate(self):
        if not self._running or not self.root.winfo_exists():
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50:
            if self._running:
                self.root.after(33, self.animate)
            return

        cx, cy = w / 2, h / 2
        ea = self.ea_var.get()
        pc = self.pc_var.get()
        o2 = self.o2_var.get()
        qa = self.qa_var.get()
        freq = self.freq_var.get()

        self.time_step += 0.03 * self.speed_var.get()
        if self.is_rotating.get():
            self.rotation_angle += 0.015 * self.speed_var.get()

        self.canvas.delete("all")

        # FPS
        self._frame_count += 1
        if time.time() - self._last_fps_time > 0.5:
            fps = self._frame_count / (time.time() - self._last_fps_time)
            self.fps_lbl.config(text=f"FPS: {fps:.0f}")
            self._last_fps_time = time.time()
            self._frame_count = 0
            self.timer_lbl.config(text=f"Task: {round(time.time() - self.task_start, 1)}s | Session: {round(time.time() - self.session_start, 1)}s")

        # --- Center Attractor Glow (Mellon Collie blue) ---
        pulse = 14 + 5 * math.sin(self.time_step * 2.5)
        if self.glow_mode.get():
            for r in range(4):
                alpha = 4 - r
                self.canvas.create_oval(cx - pulse * (1 + r * 0.4), cy - pulse * (1 + r * 0.4),
                                        cx + pulse * (1 + r * 0.4), cy + pulse * (1 + r * 0.4),
                                        outline="#00e5ff", width=1, stipple="")
        self.canvas.create_oval(cx - pulse, cy - pulse, cx + pulse, cy + pulse, outline="#ffffff", width=2)

        # --- WAVES (from v2) ---
        if self.show_waves.get():
            num_lines = int(16 + o2 * 1.8)
            for i in range(num_lines):
                t = i / max(1, num_lines - 1)
                base_angle = (t * math.pi * 2) * (pc / 10.0) + self.rotation_angle
                length = (min(w, h) * 0.38) * (1 + ea / 22.0)

                x_end = cx + length * math.cos(base_angle)
                y_end = cy - length * math.sin(base_angle)

                # faint ray
                self.canvas.create_line(cx, cy, x_end, y_end, fill="#182a6a", width=1)

                # wavy overlay
                wave_pts = []
                steps = 36
                for s in range(steps):
                    st = s / steps
                    curr_x = cx + (x_end - cx) * st
                    curr_y = cy + (y_end - cy) * st
                    offset = math.sin(st * freq * math.pi + i * 0.22 + self.rotation_angle * 1.5) * (qa * 2.6) * (ea / 10.0)
                    perp_x = curr_x - offset * math.sin(base_angle)
                    perp_y = curr_y - offset * math.cos(base_angle)
                    wave_pts.extend([perp_x, perp_y])

                if len(wave_pts) >= 4:
                    hue = int((i * 11 + qa * 3) % 180 + 70)  # blue-purple range
                    col = f"#{hue:02x}{220:02x}ff" if self.glow_mode.get() else "#ffffff"
                    self.canvas.create_line(*wave_pts, fill=col, width=1 if not self.glow_mode.get() else 2, smooth=True)

        # --- PARTICLES (from v1) ---
        if self.show_particles.get():
            max_hist = int(o2 * 1.6) + 2
            for p in self.particles:
                dx = cx - p["x"]
                dy = cy - p["y"]
                dist = math.hypot(dx, dy) + 0.1
                force = (pc * 0.16) / (dist**0.5)
                fx = (dx / dist) * force
                fy = (dy / dist) * force

                wave = math.sin(dist * 0.05 - self.time_step * 3) * (qa * 0.11)
                perp_x = -(dy / dist) * wave
                perp_y = (dx / dist) * wave

                p["vx"] = (p["vx"] + fx + perp_x) * 0.96
                p["vy"] = (p["vy"] + fy + perp_y) * 0.96
                p["x"] += p["vx"] * (ea * 0.28)
                p["y"] += p["vy"] * (ea * 0.28)

                p["history"].append((p["x"], p["y"]))
                if len(p["history"]) > max_hist:
                    p["history"].pop(0)

                if len(p["history"]) > 1:
                    flat = []
                    for pt in p["history"]:
                        flat.extend(pt)
                    hue = int((dist + qa * 5 + p["hue_offset"]) % 200 + 20)
                    # Mellon Collie palette: blues to purples
                    r = int(100 + 100 * math.sin(hue * 0.02))
                    g = int(200 + hue * 0.2) % 255
                    b = 255
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    self.canvas.create_line(*flat, fill=color, width=1, smooth=True, capstyle=tk.ROUND)

                self.canvas.create_oval(p["x"] - 2, p["y"] - 2, p["x"] + 2, p["y"] + 2, fill="#ffffff", outline="")

        if self._running:
            self.root.after(30, self.animate)


if __name__ == "__main__":
    root = tk.Tk()
    # grunge font fallback
    try:
        root.option_add("*Font", "Courier 9")
    except Exception:
        pass
    app = QualiaFusionV3(root)
    root.mainloop()
