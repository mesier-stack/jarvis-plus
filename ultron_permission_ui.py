from __future__ import annotations

import customtkinter as ctk

_ACTIONS = ("vision", "files", "close_window", "power", "watch", "microphone", "visual_click")
_VALUES = ("allow", "ask", "deny")


def install_permission_ui(app_cls) -> None:
    if getattr(app_cls, "_ultron_permission_ui_installed", False):
        return
    original_header = app_cls._build_header

    def build_header(self):
        original_header(self)
        try:
            self._top_button(self.wake_btn.master, "PERMS", self._open_permission_center).pack(side="left", padx=3)
        except Exception:
            self.bind("<Control-Shift-L>", lambda _e: self._open_permission_center())

    def open_center(self):
        win = ctk.CTkToplevel(self)
        win.title("ULTRON // PERMISSION CENTER")
        win.geometry("720x560")
        win.configure(fg_color="#030304")
        ctk.CTkLabel(win, text="PERMISSION CENTER", text_color="#FF3142", font=ctk.CTkFont("Consolas", 20, "bold")).pack(anchor="w", padx=20, pady=(18, 6))
        ctk.CTkLabel(win, text="ALLOW = no prompt  //  ASK = confirm first  //  DENY = blocked", text_color="#85858D", font=ctk.CTkFont("Consolas", 9)).pack(anchor="w", padx=20, pady=(0, 12))
        frame = ctk.CTkScrollableFrame(win, fg_color="#09090B")
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        for action in _ACTIONS:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=6)
            ctk.CTkLabel(row, text=action.upper(), width=180, anchor="w", text_color="#F5F5F7", font=ctk.CTkFont("Consolas", 10, "bold")).pack(side="left")
            current = self.brain.memory.get_setting(f"permission_{action}", "ask")
            menu = ctk.CTkOptionMenu(row, values=list(_VALUES), width=130)
            menu.set(current if current in _VALUES else "ask")
            menu.configure(command=lambda value, a=action: self.brain.memory.set_setting(f"permission_{a}", value))
            menu.pack(side="right")

    app_cls._build_header = build_header
    app_cls._open_permission_center = open_center
    app_cls._ultron_permission_ui_installed = True
