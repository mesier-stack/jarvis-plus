from __future__ import annotations

import threading
import customtkinter as ctk


def install_conversation_mode(app_cls) -> None:
    if getattr(app_cls, "_ultron_conversation_installed", False):
        return

    original_init = app_cls.__init__
    original_handle_reply = app_cls._handle_reply
    original_close = app_cls._close

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.conversation_mode = False
        self.conversation_turns_left = 0
        self.bind("<Control-Shift-c>", lambda _e: self._toggle_conversation_mode())
        try:
            btn = ctk.CTkButton(
                self,
                text="CONVERSE: OFF",
                command=self._toggle_conversation_mode,
                width=120,
                height=28,
                corner_radius=3,
                fg_color="transparent",
                border_width=1,
                border_color="#8D1D29",
                text_color="#F5F5F7",
                font=ctk.CTkFont("Consolas", 8, "bold"),
            )
            btn.place(relx=0.5, rely=0.012, anchor="n")
            self.converse_btn = btn
        except Exception:
            self.converse_btn = None

    def _toggle_conversation_mode(self):
        self.conversation_mode = not self.conversation_mode
        self.conversation_turns_left = 8 if self.conversation_mode else 0
        if getattr(self, "converse_btn", None):
            self.converse_btn.configure(text=f"CONVERSE: {'ON' if self.conversation_mode else 'OFF'}")
        self._system(
            "CONTINUOUS CONVERSATION ONLINE // 8 FOLLOW-UP TURNS"
            if self.conversation_mode
            else "CONTINUOUS CONVERSATION OFFLINE"
        )
        if self.conversation_mode and not self.processing and not self.listening:
            self.after(400, self._start_listen_once)

    def _handle_reply(self, reply):
        original_handle_reply(self, reply)
        if self.conversation_mode:
            self.conversation_turns_left -= 1
            if self.conversation_turns_left <= 0:
                self.conversation_mode = False
                if getattr(self, "converse_btn", None):
                    self.converse_btn.configure(text="CONVERSE: OFF")
                self._system("CONTINUOUS CONVERSATION SESSION COMPLETE")
                return
            def relisten():
                if self.conversation_mode and not self.processing and not self.listening:
                    self._start_listen_once()
            self.after(1200, relisten)

    def _close(self):
        self.conversation_mode = False
        return original_close(self)

    app_cls.__init__ = __init__
    app_cls._toggle_conversation_mode = _toggle_conversation_mode
    app_cls._handle_reply = _handle_reply
    app_cls._close = _close
    app_cls._ultron_conversation_installed = True
