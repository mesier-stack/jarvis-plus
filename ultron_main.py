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

APP_VERSION = "1.0"
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
        self._assistant("ULTRON core online. Voice, memory and command systems are standing by.", speak=False)
        self._system("CTRL+SPACE = PUSH TO TALK  //  F11 = FULLSCREEN")

    def _build_header(self) -> None:
        top = ctk.CTkFrame(self, height=74, corner_radius=0, fg_color=VOID)
        top.grid(row=0, column=0, sticky="ew", padx=20)
        top.grid_columnconfigure(1, weight=1)
        top.grid_propagate(False)
        left = ctk.CTkFrame(top, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", pady=12)
        ctk.CTkLabel(left, text="ULTRON", font=ctk.CTkFont("Segoe UI", 29, "bold"), text_color=WHITE).pack(side="left")
        ctk.CTkLabel(left, text=" //", font=ctk.CTkFont("Consolas", 18, "bold"), text_color=RED).pack(side="left", padx=(5, 10))
        ctk.CTkLabel(left, text=f"ADAPTIVE INTELLIGENCE CORE  //  PRIME NODE  //  v{APP_VERSION}", font=ctk.CTkFont("Consolas", 10), text_color=MUTED).pack(side="left", pady=(9, 0))
        center = ctk.CTkFrame(top, fg_color="transparent")
        center.grid(row=0, column=1)
        self.clock = ctk.CTkLabel(center, text="", font=ctk.CTkFont("Consolas", 18, "bold"), text_color=RED)
        self.clock.pack()
        self.date_label = ctk.CTkLabel(center, text="", font=ctk.CTkFont("Consolas", 9), text_color=MUTED)
        self.date_label.pack()
        right = ctk.CTkFrame(top, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e")
        self.status_badge = ctk.CTkLabel(right, text="  CORE ONLINE  ", height=28, corner_radius=4, fg_color=RED_DARK, text_color=RED, font=ctk.CTkFont("Consolas", 9, "bold"))
        self.status_badge.pack(side="left", padx=5)
        self.mic_btn = self._top_button(right, "MIC", self._start_listen_once)
        self.mic_btn.pack(side="left", padx=3)
        self.wake_btn = self._top_button(right, "WAKE: OFF", self._toggle_wake_mode)
        self.wake_btn.pack(side="left", padx=3)
        self.voice_btn = self._top_button(right, "VOICE: ON", self._toggle_voice)
        self.voice_btn.pack(side="left", padx=3)
        self._top_button(right, "F11", lambda: self._set_fullscreen(not self.fullscreen)).pack(side="left", padx=3)
        self._top_button(right, "EXIT", self._close).pack(side="left", padx=3)

    def _top_button(self, parent, text: str, command):
        return ctk.CTkButton(parent, text=text, command=command, width=78, height=30, corner_radius=3, fg_color="transparent", hover_color=RED_DARK, border_width=1, border_color=LINE_BRIGHT, text_color=WHITE, font=ctk.CTkFont("Consolas", 8, "bold"))

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
        ctk.CTkLabel(title, text="CENTRAL COGNITIVE CORE", font=ctk.CTkFont("Consolas", 11, "bold"), text_color=RED).pack(side="left", padx=14)
        self.mode_label = ctk.CTkLabel(title, text="MODE // READY", font=ctk.CTkFont("Consolas", 8), text_color=MUTED)
        self.mode_label.pack(side="right", padx=14)
        self.canvas = tk.Canvas(core_panel, bg=VOID, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        telemetry = ctk.CTkFrame(core_panel, fg_color=PANEL_ALT, corner_radius=4, border_width=1, border_color=LINE)
        telemetry.place(relx=0.025, rely=0.105, width=232, height=225)
        ctk.CTkLabel(telemetry, text="LIVE TELEMETRY", font=ctk.CTkFont("Consolas", 9, "bold"), text_color=RED).pack(anchor="w", padx=12, pady=(10, 8))
        self.cpu_label = self._metric(telemetry, "CPU LOAD")
        self.ram_label = self._metric(telemetry, "MEMORY")
        self.disk_label = self._metric(telemetry, "STORAGE")
        self.memory_label = self._metric(telemetry, "MEMORY BANK")
        self.ai_label = self._metric(telemetry, "AI PROVIDER")
        self.voice_state_label = self._metric(telemetry, "VOICE LINK")
        quick = ctk.CTkFrame(core_panel, fg_color="transparent")
        quick.place(relx=0.79, rely=0.105, relwidth=0.18)
        for label, command in (("SYSTEM SCAN", "PC status"), ("SCREENSHOT", "screenshot"), ("MEMORIES", "what do you remember about me"), ("NOTES", "show notes"), ("HELP", "what can you do")):
            ctk.CTkButton(quick, text=label, command=lambda c=command: self._quick(c), height=31, corner_radius=2, fg_color=PANEL_ALT, hover_color=RED_DARK, border_width=1, border_color=LINE_BRIGHT, text_color=WHITE, font=ctk.CTkFont("Consolas", 8, "bold")).pack(fill="x", pady=3)
        comms = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=5, border_width=1, border_color=LINE)
        comms.grid(row=0, column=1, sticky="nsew")
        comms.grid_rowconfigure(1, weight=1)
        comms.grid_columnconfigure(0, weight=1)
        comms_title = ctk.CTkFrame(comms, height=42, corner_radius=0, fg_color=PANEL_ALT)
        comms_title.grid(row=0, column=0, sticky="ew")
        comms_title.grid_propagate(False)
        ctk.CTkLabel(comms_title, text="COMMUNICATION LINK", font=ctk.CTkFont("Consolas", 11, "bold"), text_color=RED).pack(side="left", padx=14)
        self.security_label = ctk.CTkLabel(comms_title, text="PERMISSION GATE // ARMED", font=ctk.CTkFont("Consolas", 8), text_color=GREEN)
        self.security_label.pack(side="right", padx=14)
        self.chat = ctk.CTkTextbox(comms, corner_radius=0, fg_color=VOID, border_width=0, text_color=WHITE, font=ctk.CTkFont("Consolas", 12), wrap="word")
        self.chat.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.chat.configure(state="disabled")
        self.confirm_frame = ctk.CTkFrame(comms, height=54, corner_radius=3, fg_color=PANEL_HI, border_width=1, border_color=AMBER)
        self.confirm_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.confirm_frame.grid_columnconfigure(0, weight=1)
        self.confirm_text = ctk.CTkLabel(self.confirm_frame, text="", anchor="w", text_color=AMBER, font=ctk.CTkFont("Consolas", 9, "bold"))
        self.confirm_text.grid(row=0, column=0, padx=10, sticky="ew")
        ctk.CTkButton(self.confirm_frame, text="CONFIRM", width=82, command=self._confirm_pending, fg_color=RED_DARK, hover_color=RED_DIM, border_width=1, border_color=RED, font=ctk.CTkFont("Consolas", 8, "bold")).grid(row=0, column=1, padx=4, pady=8)
        ctk.CTkButton(self.confirm_frame, text="CANCEL", width=72, command=self._cancel_pending, fg_color="transparent", hover_color=PANEL_ALT, border_width=1, border_color=LINE_BRIGHT, font=ctk.CTkFont("Consolas", 8, "bold")).grid(row=0, column=2, padx=(0, 8), pady=8)
        self.confirm_frame.grid_remove()

    def _metric(self, parent, label: str):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=27)
        row.pack(fill="x", padx=12)
        row.pack_propagate(False)
        ctk.CTkLabel(row, text=label, font=ctk.CTkFont("Consolas", 8), text_color=MUTED).pack(side="left")
        value = ctk.CTkLabel(row, text="--", font=ctk.CTkFont("Consolas", 8, "bold"), text_color=RED)
        value.pack(side="right")
        return value

    def _build_command_bar(self) -> None:
        bar = ctk.CTkFrame(self, height=68, corner_radius=0, fg_color=PANEL_ALT, border_width=1, border_color=LINE)
        bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 18))
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_propagate(False)
        ctk.CTkLabel(bar, text=">", font=ctk.CTkFont("Consolas", 19, "bold"), text_color=RED).grid(row=0, column=0, padx=(16, 8), pady=14)
        self.entry = ctk.CTkEntry(bar, placeholder_text="Issue directive...", height=38, corner_radius=2, fg_color=VOID, border_width=1, border_color=LINE_BRIGHT, text_color=WHITE, placeholder_text_color=MUTED, font=ctk.CTkFont("Consolas", 12))
        self.entry.grid(row=0, column=1, sticky="ew", pady=13)
        self.entry.bind("<Return>", lambda _e: self._submit())
        self.send_btn = ctk.CTkButton(bar, text="EXECUTE", command=self._submit, width=110, height=38, corner_radius=2, fg_color=RED_DARK, hover_color=RED_DIM, border_width=1, border_color=RED, text_color=WHITE, font=ctk.CTkFont("Consolas", 10, "bold"))
        self.send_btn.grid(row=0, column=2, padx=(12, 5))
        self.ptt_btn = ctk.CTkButton(bar, text="TALK", command=self._start_listen_once, width=78, height=38, corner_radius=2, fg_color="transparent", hover_color=RED_DARK, border_width=1, border_color=LINE_BRIGHT, text_color=RED, font=ctk.CTkFont("Consolas", 9, "bold"))
        self.ptt_btn.grid(row=0, column=3, padx=(4, 12))

    def _submit(self) -> None:
        if self.processing:
            return
        text = self.entry.get().strip()
        if text:
            self.entry.delete(0, "end")
            self._dispatch(text)

    def _dispatch(self, text: str) -> None:
        if self.processing:
            return
        self._user(text)
        self.processing = True
        self.activity = 1.0
        self.send_btn.configure(text="PROCESSING", state="disabled")
        self.status_badge.configure(text="  THINKING  ", text_color=AMBER)
        self.mode_label.configure(text="MODE // COGNITION", text_color=AMBER)
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _quick(self, command: str) -> None:
        if not self.processing:
            self._dispatch(command)

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
                    self._handle_reply(payload)
                elif kind == "heard":
                    heard = str(payload).strip()
                    if heard:
                        self._system(f"VOICE INPUT // {heard}")
                        self._dispatch(heard)
                elif kind == "wake_heard":
                    self._handle_wake_phrase(str(payload).strip())
                elif kind == "listen_error":
                    self._system(f"MICROPHONE // {payload}")
                else:
                    self._assistant(f"Core fault: {payload}", speak=False)
                    self._finish_processing()
        except queue.Empty:
            pass
        self.after(70, self._drain_inbox)

    def _handle_reply(self, reply: object) -> None:
        text = getattr(reply, "text", str(reply))
        confirmation = getattr(reply, "requires_confirmation", None)
        self._assistant(text, speak=not bool(confirmation))
        if confirmation:
            self.pending_confirmation = str(confirmation)
            self.confirm_text.configure(text=f"AUTHORIZATION REQUIRED // {confirmation}")
            self.confirm_frame.grid()
            self.security_label.configure(text="PERMISSION GATE // WAITING", text_color=AMBER)
        self._finish_processing()

    def _finish_processing(self) -> None:
        self.processing = False
        self.send_btn.configure(text="EXECUTE", state="normal")
        self.status_badge.configure(text="  CORE ONLINE  ", text_color=RED)
        self.mode_label.configure(text="MODE // READY", text_color=MUTED)

    def _confirm_pending(self) -> None:
        if not self.pending_confirmation:
            return
        command = self.pending_confirmation
        self._system(f"AUTHORIZATION GRANTED // {command}")
        self.pending_confirmation = None
        self.confirm_frame.grid_remove()
        self.security_label.configure(text="PERMISSION GATE // ARMED", text_color=GREEN)
        self._dispatch("yes, confirm")

    def _cancel_pending(self) -> None:
        if self.pending_confirmation:
            self._system("AUTHORIZATION DENIED // ACTION CANCELLED")
        self.pending_confirmation = None
        self.confirm_frame.grid_remove()
        self.security_label.configure(text="PERMISSION GATE // ARMED", text_color=GREEN)

    def _start_listen_once(self) -> None:
        if self.listening or self.processing:
            return
        self.listening = True
        self.status_badge.configure(text="  LISTENING  ", text_color=GREEN)
        self.mode_label.configure(text="MODE // AUDIO CAPTURE", text_color=GREEN)
        self.mic_btn.configure(text="LISTEN...")
        self.ptt_btn.configure(text="LISTEN...")
        threading.Thread(target=self._listen_once_worker, daemon=True).start()

    def _listen_once_worker(self) -> None:
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            recognizer.dynamic_energy_threshold = True
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.45)
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)
            try:
                text = recognizer.recognize_google(audio, language="es-CL")
            except sr.UnknownValueError:
                try:
                    text = recognizer.recognize_google(audio, language="en-US")
                except sr.UnknownValueError:
                    text = ""
            self.inbox.put(("heard", text)) if text else self.inbox.put(("listen_error", "I couldn't understand that."))
        except Exception as exc:
            self.inbox.put(("listen_error", str(exc)))
        finally:
            self.listening = False
            self.after(0, self._reset_listen_ui)

    def _reset_listen_ui(self) -> None:
        if not self.processing:
            self.status_badge.configure(text="  CORE ONLINE  ", text_color=RED)
            self.mode_label.configure(text="MODE // READY", text_color=MUTED)
        self.mic_btn.configure(text="MIC")
        self.ptt_btn.configure(text="TALK")

    def _toggle_wake_mode(self) -> None:
        self.wake_mode = not self.wake_mode
        self.wake_btn.configure(text=f"WAKE: {'ON' if self.wake_mode else 'OFF'}")
        self._system(f"WAKE WORD // {'ACTIVE' if self.wake_mode else 'DISABLED'}")
        if self.wake_mode:
            threading.Thread(target=self._wake_loop, daemon=True).start()

    def _wake_loop(self) -> None:
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            recognizer.dynamic_energy_threshold = True
            while self.wake_mode:
                if self.processing or self.listening:
                    threading.Event().wait(0.35)
                    continue
                try:
                    with sr.Microphone() as source:
                        audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                    try:
                        phrase = recognizer.recognize_google(audio, language="es-CL")
                    except sr.UnknownValueError:
                        phrase = ""
                    if phrase:
                        self.inbox.put(("wake_heard", phrase))
                except sr.WaitTimeoutError:
                    continue
                except Exception as exc:
                    self.inbox.put(("listen_error", f"Wake mode stopped: {exc}"))
                    self.wake_mode = False
                    self.after(0, lambda: self.wake_btn.configure(text="WAKE: OFF"))
        except Exception as exc:
            self.inbox.put(("listen_error", f"Wake mode unavailable: {exc}"))
            self.wake_mode = False

    def _handle_wake_phrase(self, phrase: str) -> None:
        low = phrase.lower().strip()
        triggers = ("ultron", "ultrón", "hey ultron", "oye ultron")
        if not any(t in low for t in triggers):
            return
        cleaned = low
        for t in triggers:
            if t in cleaned:
                cleaned = cleaned.replace(t, "", 1).strip(" ,.!?:;")
                break
        self.activity = 1.0
        if cleaned:
            self._system(f"WAKE DETECTED // {phrase}")
            self._dispatch(cleaned)
        else:
            self._assistant("Listening.", speak=True)
            self.after(250, self._start_listen_once)

    def _append(self, prefix: str, text: str, color: str) -> None:
        self.chat.configure(state="normal")
        tag = f"tag_{prefix}_{random.randint(1, 999999)}"
        self.chat.tag_config(tag, foreground=color)
        self.chat.insert("end", f"\n{prefix}\n", tag)
        self.chat.insert("end", f"{text}\n")
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def _user(self, text: str) -> None:
        self._append("DIRECTIVE", text, WHITE)

    def _assistant(self, text: str, speak: bool) -> None:
        self._append("ULTRON", text, RED)
        if speak and self.voice_enabled:
            threading.Thread(target=self.voice.speak, args=(text,), daemon=True).start()

    def _system(self, text: str) -> None:
        self._append("SYSTEM", text, MUTED)

    def _toggle_voice(self) -> None:
        self.voice_enabled = not self.voice_enabled
        self.voice_btn.configure(text=f"VOICE: {'ON' if self.voice_enabled else 'OFF'}")
        self._system(f"VOICE OUTPUT // {'ENABLED' if self.voice_enabled else 'MUTED'}")

    def _tick_clock(self) -> None:
        now = datetime.now()
        self.clock.configure(text=now.strftime("%H:%M:%S"))
        self.date_label.configure(text=now.strftime("%A // %d %B %Y").upper())
        self.after(250, self._tick_clock)

    def _refresh_metrics(self) -> None:
        try:
            import os
            import psutil
            self.cpu_label.configure(text=f"{psutil.cpu_percent():.0f}%")
            self.ram_label.configure(text=f"{psutil.virtual_memory().percent:.0f}%")
            root = "C:\\" if os.name == "nt" else "/"
            self.disk_label.configure(text=f"{psutil.disk_usage(root).percent:.0f}%")
        except Exception:
            self.cpu_label.configure(text="ONLINE")
            self.ram_label.configure(text="ONLINE")
            self.disk_label.configure(text="ONLINE")
        try:
            self.memory_label.configure(text=str(len(self.brain.memory.list_memories(99))))
        except Exception:
            self.memory_label.configure(text="--")
        try:
            self.ai_label.configure(text=self.brain.ai.provider.upper())
        except Exception:
            self.ai_label.configure(text="LOCAL")
        voice_state = "CLOUD" if getattr(self.voice, "cloud_available", False) else ("LOCAL" if getattr(self.voice, "available", False) else "TEXT")
        self.voice_state_label.configure(text=voice_state)
        self.after(1200, self._refresh_metrics)

    def _animate_core(self) -> None:
        c = self.canvas
        w = max(c.winfo_width(), 2)
        h = max(c.winfo_height(), 2)
        c.delete("all")
        cx, cy = w / 2, h / 2
        base = min(w, h)
        for sx, sy, radius in self.stars:
            x, y = sx * w, sy * h
            c.create_oval(x, y, x + radius, y + radius, fill="#241014", outline="")
        self.angle = (self.angle + (1.7 if self.processing else 0.65)) % 360
        self.pulse += 0.085 if self.processing else 0.045
        self.activity *= 0.96
        pulse = (math.sin(self.pulse) + 1) / 2
        boost = 1.0 + self.activity * 0.15
        for idx, ratio in enumerate((0.39, 0.31, 0.235)):
            r = base * ratio * boost
            c.create_oval(cx-r, cy-r, cx+r, cy+r, outline=LINE_BRIGHT if idx == 0 else LINE, width=2 if idx == 0 else 1)
        ring = base * 0.33
        for i in range(24):
            start = self.angle + i * 15
            if i % 3 != 0:
                c.create_arc(cx-ring, cy-ring, cx+ring, cy+ring, start=start, extent=8, style="arc", outline=RED_DIM, width=2)
        iris = base * (0.125 + pulse * 0.01 + self.activity * 0.012)
        c.create_oval(cx-iris*1.55, cy-iris, cx+iris*1.55, cy+iris, fill="#160408", outline=RED_DIM, width=2)
        pupil = iris * (0.42 if not self.listening else 0.30)
        c.create_oval(cx-pupil, cy-pupil, cx+pupil, cy+pupil, fill=RED_DARK, outline=RED, width=2)
        glow = pupil * (0.35 + pulse * 0.12)
        c.create_oval(cx-glow, cy-glow, cx+glow, cy+glow, fill=RED, outline="")
        tick_r = base * 0.42
        for deg in range(0, 360, 30):
            a = math.radians(deg + self.angle * 0.15)
            x1, y1 = cx + math.cos(a)*tick_r, cy + math.sin(a)*tick_r
            x2, y2 = cx + math.cos(a)*(tick_r+9), cy + math.sin(a)*(tick_r+9)
            c.create_line(x1, y1, x2, y2, fill=LINE_BRIGHT)
        state = "LISTENING" if self.listening else ("PROCESSING" if self.processing else "ONLINE")
        c.create_text(cx, cy + base*0.19, text=f"ULTRON // {state}", fill=RED if state != "ONLINE" else WHITE, font=("Consolas", 12, "bold"))
        c.create_text(cx, cy + base*0.235, text="PRIME COGNITIVE NODE", fill=MUTED, font=("Consolas", 8))
        self.after(30, self._animate_core)

    def _set_fullscreen(self, enabled: bool) -> None:
        self.fullscreen = bool(enabled)
        self.attributes("-fullscreen", self.fullscreen)

    def _close(self) -> None:
        self.wake_mode = False
        try:
            if hasattr(self.voice, "stop"):
                self.voice.stop()
        except Exception:
            pass
        self.destroy()


if __name__ == "__main__":
    UltronApp().mainloop()
