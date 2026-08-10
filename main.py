from __future__ import annotations

import math
import os
import queue
import random
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog

import customtkinter as ctk

from jarvis_core import (
    AIClient,
    JarvisBrain,
    SystemActions,
    VoiceEngine,
    configure_ai_key,
    configure_voice_id,
    verify_elevenlabs_key,
    watch_reminders,
)
from updater import UpdateClient, UpdateInfo
from version import VERSION


ctk.set_appearance_mode("dark")

VOID = "#001014"
PANEL = "#021A21"
PANEL_ALT = "#03262E"
LINE = "#0C5662"
LINE_SOFT = "#073640"
CYAN = "#8DEFF1"
CYAN_DIM = "#178A97"
BLUE = "#31C8D4"
VIOLET = "#63D3D7"
WHITE = "#EDFFFF"
MUTED = "#4F8D94"
GREEN = "#4CFFB0"
AMBER = "#D8C64A"
RED = "#FF577B"


class JarvisApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("J.A.R.V.I.S. // Circular Intelligence Interface")
        self.geometry("1440x900")
        self.minsize(1100, 700)
        self.configure(fg_color=VOID)
        self.attributes("-fullscreen", True)

        self.brain = JarvisBrain()
        language = self.brain.memory.get_setting("voice_language", "auto")
        speed = self.brain.memory.get_setting("voice_speed", "fast")
        self.voice = VoiceEngine(language, speed)
        self.stop_event = threading.Event()
        self.inbox: queue.Queue[tuple[str, object]] = queue.Queue()
        self.angle = 0.0
        self.listening = False
        self.wake_mode = False
        self.fullscreen = True
        self.update_client = UpdateClient()
        self.update_info: UpdateInfo | None = None
        self.stars = [(random.random(), random.random(), random.choice((1, 1, 1, 2))) for _ in range(85)]

        self.bind("<Escape>", lambda _event: self._set_fullscreen(False))
        self.bind("<F11>", lambda _event: self._set_fullscreen(not self.fullscreen))
        self._build_ui()
        self.after(30, self._animate_hud)
        self.after(80, self._drain_inbox)
        self.after(250, self._tick_clock)
        self.after(700, self._update_metrics)
        self.after(2500, lambda: self._check_updates(manual=False))
        threading.Thread(
            target=watch_reminders,
            args=(self.brain.memory, self._reminder_from_thread, self.stop_event),
            daemon=True,
        ).start()
        self.protocol("WM_DELETE_WINDOW", self._close)

        intro = "Cinematic interface online. Good evening, Dante. How may I assist?"
        if self.voice.cloud_available:
            intro += " The voice you hear is AI-generated."
        self._assistant_message(intro, speak=False)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build_top_hud()

        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 8))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)
        self._build_reactor(body)
        self._build_comms(body)
        self._build_command_bar()

    def _build_top_hud(self) -> None:
        top = ctk.CTkFrame(self, height=72, corner_radius=0, fg_color=VOID)
        top.grid(row=0, column=0, sticky="ew", padx=20)
        top.grid_columnconfigure(1, weight=1)
        top.grid_propagate(False)

        brand = ctk.CTkFrame(top, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="w", pady=12)
        ctk.CTkLabel(
            brand, text="J.A.R.V.I.S.", font=ctk.CTkFont("Segoe UI", 25, "bold"), text_color=WHITE
        ).pack(side="left")
        ctk.CTkLabel(
            brand, text="  //", font=ctk.CTkFont("Consolas", 18, "bold"), text_color=AMBER
        ).pack(side="left", padx=(4, 12))
        ctk.CTkLabel(
            brand,
            text=f"CIRCULAR INTELLIGENCE CORE  //  MK IV  //  v{VERSION}",
            font=ctk.CTkFont("Consolas", 10),
            text_color=MUTED,
        ).pack(side="left", pady=(8, 0))

        center = ctk.CTkFrame(top, fg_color="transparent")
        center.grid(row=0, column=1)
        self.clock = ctk.CTkLabel(
            center, text="", font=ctk.CTkFont("Consolas", 18, "bold"), text_color=CYAN
        )
        self.clock.pack()
        self.date_label = ctk.CTkLabel(
            center, text="", font=ctk.CTkFont("Consolas", 9), text_color=MUTED
        )
        self.date_label.pack()

        controls = ctk.CTkFrame(top, fg_color="transparent")
        controls.grid(row=0, column=2, sticky="e")
        provider = self.brain.ai.provider.upper()
        self.provider_badge = ctk.CTkLabel(
            controls,
            text=f"  {provider} CORE  ",
            height=28,
            corner_radius=4,
            fg_color="#08333A" if provider != "LOCAL" else PANEL_ALT,
            text_color=GREEN if provider != "LOCAL" else AMBER,
            font=ctk.CTkFont("Consolas", 9, "bold"),
        )
        self.provider_badge.pack(side="left", padx=8)
        self._top_button(controls, "AI SETUP", self._setup_ai, VIOLET).pack(side="left", padx=4)
        self._top_button(controls, "VOICE SETUP", self._setup_voice, CYAN).pack(side="left", padx=4)
        self._top_button(controls, "FULLSCREEN", lambda: self._set_fullscreen(not self.fullscreen)).pack(
            side="left", padx=4
        )
        self.update_btn = self._top_button(controls, "UPDATE", lambda: self._check_updates(manual=True), GREEN)
        self.update_btn.pack(side="left", padx=4)
        self._top_button(controls, "EXIT", self._close, RED).pack(side="left", padx=4)

    def _top_button(self, parent, text: str, command, color: str = CYAN):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=86,
            height=30,
            corner_radius=4,
            fg_color="transparent",
            hover_color="#07313A",
            border_width=1,
            border_color=LINE,
            text_color=color,
            font=ctk.CTkFont("Consolas", 9, "bold"),
        )

    def _hud_panel(self, parent, width: int):
        panel = ctk.CTkFrame(
            parent,
            width=width,
            corner_radius=6,
            fg_color=PANEL,
            border_width=1,
            border_color=LINE_SOFT,
        )
        panel.grid_propagate(False)
        return panel

    def _section_title(self, parent, text: str, code: str) -> None:
        row = ctk.CTkFrame(parent, height=42, corner_radius=0, fg_color=PANEL_ALT)
        row.pack(fill="x", padx=1, pady=(1, 12))
        row.pack_propagate(False)
        ctk.CTkLabel(
            row, text=text, font=ctk.CTkFont("Consolas", 11, "bold"), text_color=CYAN
        ).pack(side="left", padx=14)
        ctk.CTkLabel(
            row, text=code, font=ctk.CTkFont("Consolas", 8), text_color=MUTED
        ).pack(side="right", padx=14)

    def _build_left_hud(self, parent) -> None:
        panel = self._hud_panel(parent, 305)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._section_title(panel, "SYSTEM OVERVIEW", "SYS.01")

        self.cpu_value, self.cpu_bar = self._metric(panel, "PROCESSOR LOAD", CYAN)
        self.ram_value, self.ram_bar = self._metric(panel, "MEMORY ARRAY", BLUE)
        self.disk_value, self.disk_bar = self._metric(panel, "STORAGE CORE", VIOLET)

        ctk.CTkLabel(
            panel, text="ACTIVE MODULES", font=ctk.CTkFont("Consolas", 9, "bold"), text_color=MUTED
        ).pack(anchor="w", padx=17, pady=(22, 7))
        voice_label = "DEEP CINEMATIC" if self.voice.cloud_available else (
            "WINDOWS LOCAL" if self.voice.available else "TEXT ONLY"
        )
        self._module(panel, "VOICE SYNTHESIS", voice_label, CYAN)
        self._module(panel, "PRIVATE MEMORY", "ENCRYPTED LOCAL", GREEN)
        self._module(panel, "ADAPTIVE LEARNING", "MONITORING", VIOLET)
        self._module(panel, "SAFETY GATE", "ARMED", AMBER)

        learning = ctk.CTkFrame(panel, fg_color="#071522", corner_radius=4, border_width=1, border_color=LINE)
        learning.pack(fill="x", padx=14, pady=(22, 10))
        ctk.CTkLabel(
            learning, text="LEARNING MATRIX", font=ctk.CTkFont("Consolas", 9, "bold"), text_color=VIOLET
        ).pack(anchor="w", padx=12, pady=(11, 2))
        self.learning_value = ctk.CTkLabel(
            learning, text="0 CORRECTIONS", font=ctk.CTkFont("Segoe UI", 18, "bold"), text_color=WHITE
        )
        self.learning_value.pack(anchor="w", padx=12)
        self.learning_sub = ctk.CTkLabel(
            learning, text="Awaiting operational feedback", font=ctk.CTkFont("Consolas", 8), text_color=MUTED
        )
        self.learning_sub.pack(anchor="w", padx=12, pady=(0, 11))

        quick = ctk.CTkFrame(panel, fg_color="transparent")
        quick.pack(side="bottom", fill="x", padx=14, pady=14)
        for label, command in (
            ("SYSTEM SCAN", "PC status"),
            ("OPEN FILES", "open files"),
            ("SCREEN CAPTURE", "screenshot"),
            ("LEARNING REPORT", "learning report"),
        ):
            ctk.CTkButton(
                quick,
                text=label,
                command=lambda cmd=command: self._send_quick(cmd),
                height=34,
                corner_radius=3,
                fg_color=PANEL_ALT,
                hover_color="#0B2235",
                border_width=1,
                border_color=LINE,
                text_color=WHITE,
                font=ctk.CTkFont("Consolas", 9, "bold"),
            ).pack(fill="x", pady=3)

    def _metric(self, parent, name: str, color: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=17, pady=(7, 3))
        ctk.CTkLabel(row, text=name, font=ctk.CTkFont("Consolas", 9), text_color=MUTED).pack(side="left")
        value = ctk.CTkLabel(
            row, text="--%", font=ctk.CTkFont("Consolas", 9, "bold"), text_color=color
        )
        value.pack(side="right")
        bar = ctk.CTkProgressBar(parent, height=5, corner_radius=0, fg_color=LINE_SOFT, progress_color=color)
        bar.pack(fill="x", padx=17)
        bar.set(0)
        return value, bar

    def _module(self, parent, label: str, value: str, color: str) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent", height=29)
        row.pack(fill="x", padx=17)
        row.pack_propagate(False)
        ctk.CTkLabel(row, text="◆", font=ctk.CTkFont("Arial", 7), text_color=color).pack(side="left")
        ctk.CTkLabel(row, text=label, font=ctk.CTkFont("Consolas", 8), text_color=MUTED).pack(
            side="left", padx=7
        )
        ctk.CTkLabel(row, text=value, font=ctk.CTkFont("Consolas", 8, "bold"), text_color=color).pack(
            side="right"
        )

    def _build_reactor(self, parent) -> None:
        center = ctk.CTkFrame(parent, fg_color="transparent")
        center.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(0, weight=1)

        self.reactor = tk.Canvas(center, bg=VOID, highlightthickness=0)
        self.reactor.grid(row=0, column=0, sticky="nsew")

        telemetry = ctk.CTkFrame(
            center, width=220, fg_color="#031E25", corner_radius=4,
            border_width=1, border_color=LINE_SOFT
        )
        telemetry.grid(row=0, column=0, sticky="nw", padx=16, pady=16)
        telemetry.grid_propagate(False)
        ctk.CTkLabel(
            telemetry, text="LIVE TELEMETRY", font=ctk.CTkFont("Consolas", 9, "bold"),
            text_color=AMBER
        ).pack(anchor="w", padx=12, pady=(10, 4))
        self.cpu_value, self.cpu_bar = self._metric(telemetry, "CPU", CYAN)
        self.ram_value, self.ram_bar = self._metric(telemetry, "MEMORY", BLUE)
        self.disk_value, self.disk_bar = self._metric(telemetry, "STORAGE", AMBER)
        self.learning_value = ctk.CTkLabel(
            telemetry, text="0 CORRECTIONS", font=ctk.CTkFont("Consolas", 9, "bold"),
            text_color=WHITE
        )
        self.learning_value.pack(anchor="w", padx=12, pady=(10, 0))
        self.learning_sub = ctk.CTkLabel(
            telemetry, text="adaptive memory online", font=ctk.CTkFont("Consolas", 7),
            text_color=MUTED
        )
        self.learning_sub.pack(anchor="w", padx=12, pady=(0, 10))

        quick = ctk.CTkFrame(center, fg_color="transparent")
        quick.grid(row=0, column=0, sticky="ne", padx=16, pady=16)
        for label, command in (
            ("SYSTEM SCAN", "PC status"),
            ("SCREENSHOT", "screenshot"),
            ("LEARNING", "learning report"),
        ):
            ctk.CTkButton(
                quick, text=label, command=lambda cmd=command: self._send_quick(cmd),
                width=108, height=29, corner_radius=2, fg_color="#03252D",
                hover_color="#07414A", border_width=1, border_color=LINE,
                text_color=CYAN, font=ctk.CTkFont("Consolas", 8, "bold")
            ).pack(pady=3)

        state = ctk.CTkFrame(center, fg_color="transparent")
        state.grid(row=0, column=0, sticky="s", pady=(0, 42))
        self.state_label = ctk.CTkLabel(
            state, text="●  SYSTEM ONLINE", font=ctk.CTkFont("Consolas", 11, "bold"), text_color=GREEN
        )
        self.state_label.pack()
        self.reactor_subtitle = ctk.CTkLabel(
            state,
            text="ADAPTIVE CORE STABLE  //  AWAITING DIRECTIVE",
            font=ctk.CTkFont("Consolas", 8),
            text_color=MUTED,
        )
        self.reactor_subtitle.pack(pady=4)

        self.waveform = tk.Canvas(center, bg=VOID, height=54, highlightthickness=0)
        self.waveform.grid(row=1, column=0, sticky="ew", padx=90)

    def _build_comms(self, parent) -> None:
        panel = self._hud_panel(parent, 420)
        panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._section_title(panel, "CONVERSATION", "LINK.07")

        self.chat_scroll = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=LINE,
            scrollbar_button_hover_color=CYAN_DIM,
        )
        self.chat_scroll.pack(fill="both", expand=True, padx=7)
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        controls = ctk.CTkFrame(panel, fg_color=PANEL_ALT, corner_radius=0, height=78)
        controls.pack(fill="x", side="bottom", padx=1, pady=1)
        controls.pack_propagate(False)
        self.voice_btn = self._small_control(controls, f"VOICE  {self.voice.speed.upper()}", self._toggle_voice)
        self.voice_btn.pack(side="left", padx=(12, 4), pady=22)
        self.wake_btn = self._small_control(controls, "WAKE  OFF", self._toggle_wake)
        self.wake_btn.pack(side="left", padx=4, pady=22)
        self._small_control(controls, "GUIDE", self._show_help).pack(side="left", padx=4, pady=22)

    def _small_control(self, parent, text: str, command):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=96,
            height=32,
            corner_radius=3,
            fg_color="#042831",
            hover_color="#07505A",
            border_width=1,
            border_color=LINE,
            text_color=CYAN,
            font=ctk.CTkFont("Consolas", 8, "bold"),
        )

    def _build_command_bar(self) -> None:
        bar = ctk.CTkFrame(
            self, height=78, corner_radius=0, fg_color=PANEL, border_width=1, border_color=LINE
        )
        bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 18))
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_propagate(False)
        ctk.CTkLabel(
            bar, text="INPUT", font=ctk.CTkFont("Consolas", 9, "bold"), text_color=AMBER
        ).grid(row=0, column=0, padx=(20, 12))
        self.entry = ctk.CTkEntry(
            bar,
            placeholder_text="Speak or type a directive…",
            height=46,
            corner_radius=3,
            border_width=1,
            border_color=LINE,
            fg_color="#001419",
            text_color=WHITE,
            placeholder_text_color=MUTED,
            font=ctk.CTkFont("Segoe UI", 12),
        )
        self.entry.grid(row=0, column=1, sticky="ew", padx=6, pady=17)
        self.entry.bind("<Return>", lambda _event: self._submit())
        self.entry.focus_set()
        self.mic_btn = ctk.CTkButton(
            bar,
            text="◉  LISTEN",
            command=self._listen,
            width=112,
            height=44,
            corner_radius=3,
            fg_color="#05343C",
            hover_color="#08606A",
            border_width=1,
            border_color=CYAN_DIM,
            text_color=CYAN,
            font=ctk.CTkFont("Consolas", 10, "bold"),
        )
        self.mic_btn.grid(row=0, column=2, padx=6)
        ctk.CTkButton(
            bar,
            text="EXECUTE  →",
            command=self._submit,
            width=130,
            height=44,
            corner_radius=3,
            fg_color=AMBER,
            hover_color="#F0DA59",
            text_color=VOID,
            font=ctk.CTkFont("Consolas", 10, "bold"),
        ).grid(row=0, column=3, padx=(6, 18))

    def _message_bubble(self, role: str, text: str, error: bool = False) -> None:
        user = role == "you"
        card = ctk.CTkFrame(
            self.chat_scroll,
            corner_radius=3,
            fg_color="#06313A" if user else PANEL_ALT,
            border_width=1,
            border_color=CYAN_DIM if user else (RED if error else LINE_SOFT),
        )
        card.grid(sticky="ew", padx=3, pady=5)
        ctk.CTkLabel(
            card,
            text=f"{'DANTE' if user else 'JARVIS+'}  //  {datetime.now():%H:%M:%S}",
            font=ctk.CTkFont("Consolas", 8, "bold"),
            text_color=CYAN if user else (RED if error else AMBER),
        ).pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(
            card,
            text=text,
            wraplength=355,
            justify="left",
            anchor="w",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=RED if error else WHITE,
        ).pack(anchor="w", padx=10, pady=(1, 9))
        self.after(30, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))

    def _assistant_message(self, text: str, error: bool = False, speak: bool = True) -> None:
        self._message_bubble("jarvis", text, error)
        if speak and not error:
            threading.Thread(target=self.voice.speak, args=(text,), daemon=True).start()

    def _send_quick(self, command: str) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, command)
        self._submit()

    def _submit(self) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self._message_bubble("you", text)
        self.state_label.configure(text="●  PROCESSING", text_color=CYAN)
        self.reactor_subtitle.configure(text="ANALYSING DIRECTIVE  //  PLEASE STAND BY")
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _process(self, text: str) -> None:
        try:
            self.inbox.put(("reply", self.brain.handle(text)))
        except Exception as exc:
            self.inbox.put(("error", str(exc)))

    def _drain_inbox(self) -> None:
        try:
            while True:
                kind, payload = self.inbox.get_nowait()
                if kind == "reply":
                    self.state_label.configure(text="●  SYSTEM ONLINE", text_color=GREEN)
                    self.reactor_subtitle.configure(text="ADAPTIVE CORE STABLE  //  AWAITING DIRECTIVE")
                    if payload.voice_language:
                        self.voice.set_language(payload.voice_language)
                    if payload.voice_speed:
                        self.voice.set_speed(payload.voice_speed)
                        self.voice_btn.configure(text=f"VOICE  {payload.voice_speed.upper()}")
                    self._assistant_message(payload.text, payload.kind == "error")
                    if payload.requires_confirmation:
                        self._confirm_power(payload.requires_confirmation)
                elif kind == "heard":
                    self.listening = False
                    self.mic_btn.configure(text="◉  LISTEN", fg_color="#09202B")
                    ok, text = payload
                    if ok:
                        self.entry.delete(0, "end")
                        self.entry.insert(0, text)
                        self._submit()
                    else:
                        self._assistant_message(text, True)
                elif kind == "reminder":
                    self._assistant_message(f"Reminder: {payload}")
                    messagebox.showinfo("JARVIS+ Reminder", str(payload))
                elif kind == "error":
                    self.state_label.configure(text="●  SYSTEM ONLINE", text_color=GREEN)
                    self.reactor_subtitle.configure(text="FAULT LOGGED  //  CORE REMAINS STABLE")
                    self._assistant_message(str(payload), True)
                elif kind == "update_available":
                    self.update_btn.configure(text="UPDATE READY", text_color=GREEN)
                    self.update_info = payload
                    notes = f"\n\n{payload.notes}" if payload.notes else ""
                    if messagebox.askyesno(
                        "JARVIS+ Update",
                        f"Version {payload.version} is available.{notes}\n\nInstall it now?",
                    ):
                        self._install_update(payload)
                elif kind == "update_none":
                    self.update_btn.configure(text="UP TO DATE", text_color=GREEN)
                    if payload:
                        self._assistant_message(f"JARVIS+ v{VERSION} is already up to date.", speak=False)
                    self.after(2500, lambda: self.update_btn.configure(text="UPDATE", text_color=GREEN))
                elif kind == "update_error":
                    self.update_btn.configure(text="UPDATE", text_color=GREEN)
                    if payload[0]:
                        if "404" in payload[1]:
                            self._assistant_message(
                                "The update channel is not online yet. Chat, voice, and local commands are unaffected.",
                                speak=False,
                            )
                        else:
                            self._assistant_message(f"Update check failed: {payload[1]}", True, speak=False)
                elif kind == "ai_ready":
                    self.brain.ai = AIClient()
                    provider = self.brain.ai.provider.upper()
                    self.provider_badge.configure(
                        text=f"  {provider} CORE  ", fg_color="#0B2832", text_color=GREEN
                    )
                    self._assistant_message(
                        "Gemini core connected. Fluent chat and cloud voice are now available."
                    )
                elif kind == "ai_error":
                    self._assistant_message(f"Gemini connection failed: {payload}", True, speak=False)
                elif kind == "voice_ready":
                    self.voice.stop()
                    self.voice = VoiceEngine(self.voice.language, self.voice.speed)
                    self._assistant_message(
                        "ElevenLabs voice connected. Low-latency cinematic speech is online."
                    )
                elif kind == "voice_error":
                    self._assistant_message(
                        f"ElevenLabs connection failed: {payload}", True, speak=False
                    )
                elif kind == "update_ready":
                    self._assistant_message("Update verified. Restarting into the new version…", speak=False)
                    self.after(450, self._close)
        except queue.Empty:
            pass
        self.after(80, self._drain_inbox)

    def _listen(self) -> None:
        if self.listening:
            return
        self.listening = True
        self.mic_btn.configure(text="◉  LISTENING", fg_color=CYAN_DIM)
        self.state_label.configure(text="●  VOICE LINK ACTIVE", text_color=CYAN)
        threading.Thread(
            target=lambda: self.inbox.put(
                ("heard", VoiceEngine.listen_once(language=self.voice.language))
            ),
            daemon=True,
        ).start()

    def _toggle_voice(self) -> None:
        self.voice.enabled = not self.voice.enabled
        if not self.voice.enabled:
            self.voice.stop()
        self.voice_btn.configure(
            text=f"VOICE  {self.voice.speed.upper() if self.voice.enabled else 'OFF'}"
        )
        self._assistant_message(
            "Voice output enabled." if self.voice.enabled else "Voice output muted.",
            speak=self.voice.enabled,
        )

    def _setup_ai(self) -> None:
        key = simpledialog.askstring(
            "JARVIS+ // Google AI Studio",
            "Paste your Gemini API key here. It stays on this PC and is never added to the app files:",
            show="•",
            parent=self,
        )
        if not key:
            return
        try:
            configure_ai_key("gemini", key)
        except ValueError as exc:
            self._assistant_message(str(exc), True, speak=False)
            return
        self.provider_badge.configure(text="  CONNECTING…  ", text_color=CYAN)

        def verify() -> None:
            try:
                client = AIClient()
                client.answer("Reply with exactly: Connected.", [{"role": "user", "content": "Connection test"}])
                self.inbox.put(("ai_ready", True))
            except Exception as exc:
                self.inbox.put(("ai_error", str(exc)))

        threading.Thread(target=verify, daemon=True).start()

    def _setup_voice(self) -> None:
        key = simpledialog.askstring(
            "JARVIS+ // ElevenLabs Voice",
            "Paste your ElevenLabs API key. It stays on this PC and is never added to JARVIS files:",
            show="•",
            parent=self,
        )
        if not key:
            return
        voice_id = simpledialog.askstring(
            "JARVIS+ // Voice Selection",
            "Voice ID (the default is an original mature British voice):",
            initialvalue=os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb"),
            parent=self,
        )
        if not voice_id:
            return

        def verify() -> None:
            try:
                verify_elevenlabs_key(key.strip())
                configure_ai_key("elevenlabs", key)
                configure_voice_id(voice_id)
                self.inbox.put(("voice_ready", True))
            except Exception as exc:
                self.inbox.put(("voice_error", str(exc)))

        threading.Thread(target=verify, daemon=True).start()

    def _toggle_wake(self) -> None:
        self.wake_mode = not self.wake_mode
        self.wake_btn.configure(text=f"WAKE  {'ON' if self.wake_mode else 'OFF'}")
        if self.wake_mode:
            threading.Thread(target=self._wake_loop, daemon=True).start()

    def _wake_loop(self) -> None:
        while self.wake_mode and not self.stop_event.is_set():
            ok, text = VoiceEngine.listen_once(
                timeout=4, phrase_time_limit=7, language=self.voice.language
            )
            if ok and "jarvis" in text.lower():
                command = text.lower().split("jarvis", 1)[1].strip(" ,")
                if command:
                    self.inbox.put(("heard", (True, command)))
            elif not ok and "timed out" not in text.lower():
                self.stop_event.wait(0.5)

    def _confirm_power(self, action: str) -> None:
        if messagebox.askyesno("JARVIS+ Security Gate", f"Authorize system {action}?"):
            ok, text = SystemActions.power_action(action)
            self._assistant_message(text, not ok)
        else:
            self._assistant_message("Authorization denied. No system changes made.")

    def _show_help(self) -> None:
        self._assistant_message(
            "Directives: open calculator · PC status · note buy the Ryzen · remind me in "
            "10 minutes to study · search RTX 5060 Chile · screenshot. Teach me with: "
            "teach launch numbers => open calculator. Press Escape to leave fullscreen or F11 to toggle it."
        )

    def _animate_hud(self) -> None:
        canvas = self.reactor
        canvas.delete("all")
        width, height = max(canvas.winfo_width(), 600), max(canvas.winfo_height(), 600)
        cx, cy = width / 2, height / 2 - 8
        base = max(175, min(width / 2 - 42, height / 2 - 28, min(width, height) * 0.405))
        pulse = 3 * math.sin(self.angle * 2.2)

        for sx, sy, size in self.stars:
            x, y = sx * width, sy * height
            canvas.create_oval(x, y, x + size, y + size, fill="#0A3840", outline="")

        canvas.create_oval(
            cx-base-58, cy-base-58, cx+base+58, cy+base+58,
            outline="#042B31", width=18
        )
        canvas.create_oval(
            cx-base-43, cy-base-43, cx+base+43, cy+base+43,
            outline="#0B5963", width=3
        )

        for i in range(72):
            a = self.angle * 0.18 + i * math.tau / 72
            inner = base + 28
            outer = base + (43 if i % 6 == 0 else 37)
            canvas.create_line(
                cx + math.cos(a) * inner, cy + math.sin(a) * inner,
                cx + math.cos(a) * outer, cy + math.sin(a) * outer,
                fill=CYAN_DIM if i % 6 == 0 else "#0A4650",
                width=2 if i % 6 == 0 else 1
            )

        for i in range(16):
            start = i * 22.5 + self.angle * 7
            canvas.create_arc(
                cx-base-24, cy-base-24, cx+base+24, cy+base+24,
                start=start, extent=16 if i % 2 == 0 else 12, style="arc",
                outline="#147884" if i % 3 else "#1B9AA5", width=14
            )

        ring_specs = (
            (base + 4, "#2CA8B2", 5, self.angle * 42, 276),
            (base - 15, "#0A525C", 13, -self.angle * 31, 248),
            (base - 35, CYAN, 5, self.angle * 54, 210),
            (base - 55, "#0C6971", 2, -self.angle * 68, 292),
        )
        for radius, color, line_width, start, extent in ring_specs:
            canvas.create_arc(
                cx-radius, cy-radius, cx+radius, cy+radius,
                start=start, extent=extent, style="arc", outline=color, width=line_width
            )

        amber_radius = base + 12
        canvas.create_arc(
            cx-amber_radius, cy-amber_radius, cx+amber_radius, cy+amber_radius,
            start=128, extent=104, style="arc", outline=AMBER, width=5
        )
        for i in range(5):
            canvas.create_arc(
                cx-base-2, cy-base-2, cx+base+2, cy+base+2,
                start=76 + i * 11, extent=5, style="arc", outline=AMBER, width=6
            )

        inner = base - 72 + pulse
        canvas.create_oval(
            cx-inner-11, cy-inner-11, cx+inner+11, cy+inner+11,
            fill="#042B31", outline="#0A5962", width=2
        )
        canvas.create_oval(
            cx-inner, cy-inner, cx+inner, cy+inner,
            fill="#001115", outline=CYAN, width=5
        )
        canvas.create_arc(
            cx-inner+16, cy-inner+16, cx+inner-16, cy+inner-16,
            start=20-self.angle*20, extent=130, style="arc", outline="#164B51", width=2
        )
        canvas.create_text(
            cx, cy-8, text="J.A.R.V.I.S.", fill=WHITE,
            font=("Segoe UI", max(22, int(base * 0.12)), "bold")
        )
        canvas.create_text(
            cx, cy+29, text="JUST A RATHER VERY INTELLIGENT SYSTEM",
            fill=MUTED, font=("Consolas", max(7, int(base * 0.032)))
        )
        canvas.create_text(
            cx, cy + base + 70, text="MK IV  //  CIRCULAR ADAPTIVE CORE",
            fill=AMBER, font=("Consolas", 8, "bold")
        )
        canvas.create_text(cx-base-70, cy-base-6, text="SYS 032.77", fill="#276C73", font=("Consolas", 7))
        canvas.create_text(cx+base+48, cy+base-4, text="CORE 100%", fill="#276C73", font=("Consolas", 7))

        self._draw_waveform()
        self.angle += 0.018 if not self.listening else 0.085
        self.after(30, self._animate_hud)

    def _draw_waveform(self) -> None:
        canvas = self.waveform
        canvas.delete("all")
        width, height = max(canvas.winfo_width(), 500), 54
        middle = height / 2
        points = []
        intensity = 16 if self.listening else 4
        for x in range(0, width + 1, 4):
            envelope = math.sin(math.pi * x / max(width, 1))
            y = middle + math.sin(x * 0.075 + self.angle * 8) * intensity * envelope
            y += math.sin(x * 0.19 - self.angle * 5) * intensity * 0.25 * envelope
            points.extend((x, y))
        canvas.create_line(0, middle, width, middle, fill="#0B2637")
        canvas.create_line(*points, fill=CYAN if self.listening else CYAN_DIM, width=2, smooth=True)

    def _tick_clock(self) -> None:
        now = datetime.now()
        self.clock.configure(text=now.strftime("%H:%M:%S"))
        self.date_label.configure(text=now.strftime("%A  //  %d %B %Y").upper())
        self.after(1000, self._tick_clock)

    def _update_metrics(self) -> None:
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("C:\\" if os.name == "nt" else "/").percent
            for value, bar, number in (
                (self.cpu_value, self.cpu_bar, cpu),
                (self.ram_value, self.ram_bar, ram),
                (self.disk_value, self.disk_bar, disk),
            ):
                value.configure(text=f"{number:.0f}%")
                bar.set(max(0, min(number / 100, 1)))
        except Exception:
            pass
        learned, uses, failures = self.brain.memory.learning_stats()
        self.learning_value.configure(text=f"{learned} CORRECTIONS")
        self.learning_sub.configure(text=f"{uses} recalled  //  {failures} misses logged")
        self.after(2000, self._update_metrics)

    def _set_fullscreen(self, enabled: bool) -> None:
        self.fullscreen = enabled
        self.attributes("-fullscreen", enabled)

    def _check_updates(self, manual: bool) -> None:
        self.update_btn.configure(text="CHECKING…", text_color=CYAN)

        def worker() -> None:
            try:
                info = self.update_client.check()
                self.inbox.put(("update_available", info) if info else ("update_none", manual))
            except Exception as exc:
                self.inbox.put(("update_error", (manual, str(exc))))

        threading.Thread(target=worker, daemon=True).start()

    def _install_update(self, info: UpdateInfo) -> None:
        self.update_btn.configure(text="DOWNLOADING…", state="disabled")

        def worker() -> None:
            try:
                self.update_client.stage_and_launch(info)
                self.inbox.put(("update_ready", info.version))
            except Exception as exc:
                self.inbox.put(("update_error", (True, str(exc))))

        threading.Thread(target=worker, daemon=True).start()

    def _reminder_from_thread(self, text: str) -> None:
        self.inbox.put(("reminder", text))

    def _close(self) -> None:
        self.stop_event.set()
        self.destroy()


if __name__ == "__main__":
    JarvisApp().mainloop()
