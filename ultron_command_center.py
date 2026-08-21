from __future__ import annotations

import customtkinter as ctk

from ultron_action_history import get_action_history
from ultron_skills import skill_summary
from ultron_telemetry_plus import telemetry_snapshot


def install_command_center(app_cls) -> None:
    if getattr(app_cls, "_ultron_command_center_installed", False):
        return
    original_header = app_cls._build_header

    def build_header(self):
        original_header(self)
        try:
            self._top_button(self.wake_btn.master, "CENTER", self._open_command_center).pack(side="left", padx=3)
        except Exception:
            self.bind("<Control-Shift-P>", lambda _e: self._open_command_center())

    def open_center(self):
        win = ctk.CTkToplevel(self)
        win.title("ULTRON // COMMAND CENTER")
        win.geometry("980x650")
        win.configure(fg_color="#030304")
        win.grid_columnconfigure((0, 1), weight=1)
        win.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(win, text="ULTRON COMMAND CENTER", text_color="#FF3142", font=ctk.CTkFont("Consolas", 20, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=18)

        left = ctk.CTkTextbox(win, fg_color="#09090B", text_color="#F5F5F7", font=ctk.CTkFont("Consolas", 11))
        left.grid(row=1, column=0, sticky="nsew", padx=(20, 8), pady=(0, 20))
        right = ctk.CTkTextbox(win, fg_color="#09090B", text_color="#F5F5F7", font=ctk.CTkFont("Consolas", 11))
        right.grid(row=1, column=1, sticky="nsew", padx=(8, 20), pady=(0, 20))

        t = telemetry_snapshot()
        left.insert("end", "LIVE SYSTEM\n\n")
        for key, value in t.items():
            left.insert("end", f"{key.upper():<10} // {value}\n")
        left.insert("end", "\nSKILL REGISTRY\n\n" + skill_summary())

        right.insert("end", "ACTION HISTORY\n\n")
        for stamp, kind, text in get_action_history(30):
            right.insert("end", f"[{stamp}] {kind}\n{text}\n\n")
        left.configure(state="disabled")
        right.configure(state="disabled")

    app_cls._build_header = build_header
    app_cls._open_command_center = open_center
    app_cls._ultron_command_center_installed = True
