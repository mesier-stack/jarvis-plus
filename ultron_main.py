from __future__ import annotations

import math
import queue
import random
import threading
import tkinter as tk
from datetime import datetime

import customtkinter as ctk

from jarvis_core import JarvisBrain, VoiceEngine


ctk.set_appearance_mode("dark")

VOID = "#050505"
PANEL = "#0B0B0C"
PANEL_ALT = "#111113"
LINE = "#3A1114"
LINE_BRIGHT = "#7D1C24"
RED = "#FF2A36"
RED_DIM = "#9E1822"
RED_DARK = "#470A0F"
WHITE = "#F4F4F4"
MUTED = "#8A8A8F"
GREEN = "#4DFF9A"
AMBER = "#FFB84D"


class UltronApp(ctk.CTk):
    """ULTRON v0.1.

    A new red/black command interface that reuses the proven local brain,
    memory, voice and safe Windows actions from JARVIS+ while keeping the
    original application untouched as a fallback.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("ULTRON // Adaptive Intelligence Core")
        self.geometry("1440x900")
        self.minsize(1100, 700)
        self.configure(fg_color=VOID)

        self.brain = JarvisBrain()
        language = self.brain.memory.get_setting("voice_language", "auto")
        speed = self.brain.memory.get_setting("voice_speed", "fast")
        profile = self.brain.memory.get_setting("voice_profile", "cinematic")
        self.voice = VoiceEngine(language, speed, profile)

        self.inbox: queue.Queue[tuple[str, object]] = queue.Queue()
        self.processing = False
        self.voice_enabled = True
        self.angle = 0.0
        self.pulse = 0.0
        self.stars = [(random.random(), random.random(), random.choice((1, 1, 2))) for _ in range(70)]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()
        self._build_command_bar()

        self.bind("<Return>", lambda _e: self._submit())
        self.bind("<Escape>", lambda _e: self.attributes("-fullscreen", False))
        self.bind("<F11>", lambda _e: self.attributes("-fullscreen", not bool(self.attributes("-fullscreen"))))

        self.after(30, self._animate_core)
        self.after(80, self._drain_inbox)
        self.after(250, self._tick_clock)
        self.after(800, self._refresh_metrics)

        self._assistant("ULTRON core online. All systems nominal. Awaiting directive.", speak=False)

    def _build_header(self) -> None:
        top = ctk.CTkFrame(self, height=72, corner_radius=0, fg_color=VOID)
        top.grid(row=0, column=0, sticky="ew", padx=20)
        top.grid_columnconfigure(1, weight=1)
        top.grid_propagate(False)

        left = ctk.CTkFrame(top, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", pady=12)
        ctk.CTkLabel(left, text="ULTRON", font=ctk.CTkFont("Segoe UI", 28, "bold"), text_color=WHITE).pack(side="left")
        ctk.CTkLabel(left, text=" //", font=ctk.CTkFont("Consolas", 18, "bold"), text_color=RED).pack(side="left", padx=(5, 10))
        ctk.CTkLabel(left, text="ADAPTIVE INTELLIGENCE CORE  //  v0.1", font=ctk.CTkFont("Consolas", 10), text_color=MUTED).pack(side="left", pady=(9, 0))

        center = ctk.CTkFrame(top, fg_color="transparent")
        center.grid(row=0, column=1)
        self.clock = ctk.CTkLabel(center, text="", font=ctk.CTkFont("Consolas", 18, "bold"), text_color=RED)
        self.clock.pack()
        self.date_label = ctk.CTkLabel(center, text="", font=ctk.CTkFont("Consolas", 9), text_color=MUTED)
        self.date_label.pack()

        right = ctk.CTkFrame(top, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e")
        self.status_badge = ctk.CTkLabel(right, text="  CORE ONLINE  ", height=28, corner_radius=4, fg_color=RED_DARK, text_color=RED, font=ctk.CTkFont("Consolas", 9, "bold"))
        self.status_badge.pack(side="left", padx=6)
        self.voice_btn = self._top_button(right, "VOICE: ON", self._toggle_voice)
        self.voice_btn.pack(side="left", padx=4)
        self._top_button(right, "FULLSCREEN", self._toggle_fullscreen).pack(side="left", padx=4)
        self._top_button(right, "EXIT", self.destroy).pack(side="left", padx=4)

    def _top_button(self, parent, text: str, command):
        return ctk.CTkButton(parent, text=text, command=command, width=92, height=30, corner_radius=3, fg_color="transparent", hover_color=RED_DARK, border_width=1, border_color=LINE_BRIGHT, text_color=WHITE, font=ctk.CTkFont("Consolas", 9, "bold"))

    def _build_body(self) -> None:
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 8))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        core_panel = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=5, border_width=1, border_color=LINE)
        core_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        core_panel.grid_rowconfigure(1, weight=1)
        core_panel.grid_columnconfigure(0, weight=1)

        title = ctk.CTkFrame(core_panel, height=42, corner_radius=0, fg_color=PANEL_ALT)
        title.grid(row=0, column=0, sticky="ew")
        title.grid_propagate(False)
        ctk.CTkLabel(title, text="CENTRAL CORE", font=ctk.CTkFont("Consolas", 11, "bold"), text_color=RED).pack(side="left", padx=14)
        ctk.CTkLabel(title, text="NODE 00 // PRIME", font=ctk.CTkFont("Consolas", 8), text_color=MUTED).pack(side="right", padx=14)

        self.canvas = tk.Canvas(core_panel, bg=VOID, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        telemetry = ctk.CTkFrame(core_panel, fg_color=PANEL_ALT, corner_radius=4, border_width=1, border_color=LINE)
        telemetry.place(relx=0.03, rely=0.10, width=220, height=190)
        ctk.CTkLabel(telemetry, text="LIVE TELEMETRY", font=ctk.CTkFont("Consolas", 9, "bold"), text_color=RED).pack(anchor="w", padx=12, pady=(10, 8))
        self.cpu_label = self._metric(telemetry, "CPU")
        self.ram_label = self._metric(telemetry, "MEMORY")
        self.disk_label = self._metric(telemetry, "STORAGE")
        self.memory_label = self._metric(telemetry, "MEMORY BANK")

        quick = ctk.CTkFrame(core_panel, fg_color="transparent")
        quick.place(relx=0.79, rely=0.10, relwidth=0.18)
        for label, command in (("SYSTEM SCAN", "PC status"), ("SCREENSHOT", "screenshot"), ("MEMORY", "what do you remember about me"), ("NOTES", "show notes")):
            ctk.CTkButton(quick, text=label, command=lambda c=command: self._quick(c), height=31, corner_radius=2, fg_color=PANEL_ALT, hover_color=RED_DARK, border_width=1, border_color=LINE_BRIGHT, text_color=WHITE, font=ctk.CTkFont("Consolas", 8, "bold")).pack(fill="x", pady=3)

        comms = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=5, border_width=1, border_color=LINE)
        comms.grid(row=0, column=1, sticky="nsew")
        comms.grid_rowconfigure(1, weight=1)
        comms.grid_columnconfigure(0, weight=1)

        comms_title = ctk.CTkFrame(comms, height=42, corner_radius=0, fg_color=PANEL_ALT)
        comms_title.grid(row=0, column=0, sticky="ew")
        comms_title.grid_propagate(False)
        ctk.CTkLabel(comms_title, text="COMMUNICATION LINK", font=ctk.CTkFont("Consolas", 11, "bold"), text_color=RED).pack(side="left", padx=14)
        ctk.CTkLabel(comms_title, text="ENCRYPTED // LOCAL MEMORY", font=ctk.CTkFont("Consolas", 8), text_color=MUTED).pack(side="right", padx=14)

        self.chat = ctk.CTkTextbox(comms, corner_radius=0, fg_color=VOID, border_width=0, text_color=WHITE, font=ctk.CTkFont("Consolas", 12), wrap="word")
        self.chat.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.chat.configure(state="disabled")

    def _metric(self, parent, label: str):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=28)
        row.pack(fill="x", padx=12)
        row.pack_propagate(False)
        ctk.CTkLabel(row, text=label, font=ctk.CTkFont("Consolas", 8), text_color=MUTED).pack(side="left")
        value = ctk.CTkLabel(row, text="--", font=ctk.CTkFont("Consolas", 8, "bold"), text_color=RED)
        value.pack(side="right")
        return value

    def _build_command_bar(self) -> None:
        bar = ctk.CTkFrame(self, height=66, corner_radius=0, fg_color=PANEL_ALT, border_width=1, border_color=LINE)
        bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 18))
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_propagate(False)

        ctk.CTkLabel(bar, text=">", font=ctk.CTkFont("Consolas", 19, "bold"), text_color=RED).grid(row=0, column=0, padx=(16, 8), pady=14)
        self.entry = ctk.CTkEntry(bar, placeholder_text="Issue directive...", height=38, corner_radius=2, fg_color=VOID, border_width=1, border_color=LINE_BRIGHT, text_color=WHITE, placeholder_text_color=MUTED, font=ctk.CTkFont("Consolas", 12))
        self.entry.grid(row=0, column=1, sticky="ew", pady=13)
        self.entry.bind("<Return>", lambda _e: self._submit())
        self.send_btn = ctk.CTkButton(bar, text="EXECUTE", command=self._submit, width=110, height=38, corner_radius=2, fg_color=RED_DARK, hover_color=RED_DIM, border_width=1, border_color=RED, text_color=WHITE, font=ctk.CTkFont("Consolas", 10, "bold"))
        self.send_btn.grid(row=0, column=2, padx=12)

    def _submit(self) -> None:
        if self.processing:
            return
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._user(text)
        self.processing = True
        self.send_btn.configure(text="PROCESSING", state="disabled")
        self.status_badge.configure(text="  THINKING  ", text_color=AMBER)
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _quick(self, command: str) -> None:
        if self.processing:
            return
        self.entry.delete(0, "end")
        self.entry.insert(0, command)
        self._submit()

    def _process(self, text: str) -> None:
        try:
            reply = self.brain.handle(text)
            self.inbox.put(("reply", reply))
        except Exception as exc:
            self.inbox.put(("error", str(exc)))

    def _drain_inbox(self) -> None:
        try:
            while True:
                kind, payload = self.inbox.get_nowait()
                if kind == "reply":
                    text = getattr(payload, "text", str(payload))
                    self._assistant(text, speak=True)
                else:
                    self._assistant(f"Core fault: {payload}", speak=False)
                self.processing = False
                self.send_btn.configure(text="EXECUTE", state="normal")
                self.status_badge.configure(text="  CORE ONLINE  ", text_color=RED)
        except queue.Empty:
            pass
        self.after(80, self._drain_inbox)

    def _append(self, prefix: str, text: str, color: str) -> None:
        self.chat.configure(state="normal")
        self.chat.insert("end", f"\n{prefix}\n", prefix)
        self.chat.tag_config(prefix, foreground=color)
        self.chat.insert("end", f"{text}\n")
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _user(self, text: str) -> None:
        self._append("DIRECTIVE", text, WHITE)

    def _assistant(self, text: str, speak: bool) -> None:
        self._append("ULTRON", text, RED)
        if speak and self.voice_enabled:
            threading.Thread(target=self.voice.speak, args=(text,), daemon=True).start()

    def _toggle_voice(self) -> None:
        self.voice_enabled = not self.voice_enabled
        self.voice_btn.configure(text=f"VOICE: {'ON' if self.voice_enabled else 'OFF'}")

    def _toggle_fullscreen(self) -> None:
        self.attributes("-fullscreen", not bool(self.attributes("-fullscreen")))

    def _tick_clock(self) -> None:
        now = datetime.now()
        self.clock.configure(text=now.strftime("%H:%M:%S"))
        self.date_label.configure(text=now.strftime("%A // %d %B %Y").upper())
        self.after(250, self._tick_clock)

    def _refresh_metrics(self) -> None:
        try:
            import psutil
            self.cpu_label.configure(text=f"{psutil.cpu_percent():.0f}%")
            self.ram_label.configure(text=f"{psutil.virtual_memory().percent:.0f}%")
            self.disk_label.configure(text=f"{psutil.disk_usage('/').percent:.0f}%")
        except Exception:
            self.cpu_label.configure(text="ONLINE")
            self.ram_label.configure(text="ONLINE")
            self.disk_label.configure(text="ONLINE")
        try:
            memories = len(self.brain.memory.list_memories(99))
            self.memory_label.configure(text=str(memories))
        except Exception:
            self.memory_label.configure(text="--")
        self.after(1200, self._refresh_metrics)

    def _animate_core(self) -> None:
        c = self.canvas
        w = max(c.winfo_width(), 2)
        h = max(c.winfo_height(), 2)
        c.delete("all")

        for sx, sy, radius in self.stars:
            x, y = sx * w, sy * h
            c.create_oval(x, y, x + radius, y + radius, fill="#261014", outline="")

        cx, cy = w / 2, h / 2
        base = min(w, h) * 0.20
        self.angle = (self.angle + 0.8) % 360
        self.pulse += 0.08
        pulse = 1 + math.sin(self.pulse) * 0.035

        for i, scale in enumerate((2.1, 1.72, 1.42, 1.12)):
            r = base * scale * pulse
            color = ("#24070A", "#4B0B10", "#7E1018", RED_DARK)[i]
            width = (1, 1, 2, 2)[i]
            c.create_oval(cx-r, cy-r, cx+r, cy+r, outline=color, width=width)

        for offset, extent in ((0, 55), (90, 42), (180, 60), (270, 35)):
            r = base * 1.72
            c.create_arc(cx-r, cy-r, cx+r, cy+r, start=self.angle + offset, extent=extent, style="arc", outline=RED, width=3)

        for offset, extent in ((20, 90), (160, 70), (285, 50)):
            r = base * 1.42
            c.create_arc(cx-r, cy-r, cx+r, cy+r, start=-self.angle * 1.35 + offset, extent=extent, style="arc", outline=RED_DIM, width=2)

        core_r = base * 0.72 * pulse
        c.create_oval(cx-core_r, cy-core_r, cx+core_r, cy+core_r, fill="#170205", outline=RED, width=2)
        pupil = core_r * 0.26
        c.create_oval(cx-pupil, cy-pupil, cx+pupil, cy+pupil, fill=RED, outline="")
        glow = pupil * (1.8 + 0.15 * math.sin(self.pulse * 1.8))
        c.create_oval(cx-glow, cy-glow, cx+glow, cy+glow, outline=RED_DIM, width=2)

        c.create_text(cx, cy + base * 1.0, text="ULTRON", fill=WHITE, font=("Consolas", 18, "bold"))
        c.create_text(cx, cy + base * 1.18, text="ADAPTIVE CORE // ACTIVE", fill=RED, font=("Consolas", 9, "bold"))

        self.after(30, self._animate_core)


if __name__ == "__main__":
    UltronApp().mainloop()
