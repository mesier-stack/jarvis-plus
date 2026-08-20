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

APP_VERSION = "1.2"
VOID = "#030304"
PANEL = "#09090B"
PANEL_ALT = "#101014"
PANEL_HI = "#15151A"
LINE = "#3C1015"
LINE_BRIGHT = "#8D1D29"
RED = "#FF3142"
RED_DIM = "#A71826"
RED_DARK = "#4A0810"
WHITE = "#F5F5F7"
MUTED = "#85858D"
GREEN = "#4DFF9A"
AMBER = "#FFB84D"


class UltronApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"ULTRON // Adaptive Intelligence Core v{APP_VERSION}")
        self.geometry("1440x900")
        self.minsize(1120, 720)
        self.configure(fg_color=VOID)

        self.brain = JarvisBrain()
        language = self.brain.memory.get_setting("voice_language", "auto")
        speed = self.brain.memory.get_setting("voice_speed", "fast")
        profile = self.brain.memory.get_setting("voice_profile", "cinematic")
        self.voice = VoiceEngine(language, speed, profile)

        self.inbox: queue.Queue[tuple[str, object]] = queue.Queue()
        self.processing = False
        self.voice_enabled = True
        self.listening = False
        self.wake_mode = False
        self.fullscreen = False
        self.pending_confirmation: str | None = None
        self.angle = 0.0
        self.pulse = 0.0
        self.activity = 0.0
        self.stars = [(random.random(), random.random(), random.choice((1, 1, 1, 2))) for _ in range(95)]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_header()
        self._build_body()
        self._build_command_bar()

        self.bind("<Escape>", lambda _e: self._set_fullscreen(False))
        self.bind("<F11>", lambda _e: self._set_fullscreen(not self.fullscreen))
        self.bind("<Control-space>", lambda _e: self._start_listen_once())

        self.after(30, self._animate_core)
        self.after(70, self._drain_inbox)
        self.after(250, self._tick_clock)
        self.after(700, self._refresh_metrics)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._assistant("ULTRON core online. Vision, voice, memory, diagnostics and focus systems are standing by.", speak=False)
        self._system("CTRL+SPACE = PUSH TO TALK  //  F11 = FULLSCREEN  //  SAY 'FOCUS MODE' FOR SHORT RESPONSES")

    def _build_header(self) -> None:
        top = ctk.CTkFrame(self, height=74, corner_radius=0, fg_color=VOID)
        top.grid(row=0, column=0, sticky="ew", padx=20)
        top.grid_columnconfigure(1, weight=1)
