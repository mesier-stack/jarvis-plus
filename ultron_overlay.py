from __future__ import annotations

import customtkinter as ctk

VOID = "#030304"
PANEL = "#09090B"
LINE = "#3C1015"
RED = "#FF3142"
RED_DARK = "#4A0810"
WHITE = "#F5F5F7"
MUTED = "#85858D"


class UltronOverlay(ctk.CTkToplevel):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.app = app
        self.title("ULTRON Overlay")
        self.geometry("660x92+340+80")
        self.resizable(False, False)
        self.configure(fg_color=VOID)
        self.attributes("-topmost", True)
        try:
            self.overrideredirect(True)
            self.attributes("-alpha", 0.96)
        except Exception:
            pass

        shell = ctk.CTkFrame(self, fg_color=PANEL, border_width=1, border_color=RED, corner_radius=8)
        shell.pack(fill="both", expand=True, padx=2, pady=2)
        shell.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(shell, text="◉", text_color=RED, font=ctk.CTkFont("Segoe UI", 28, "bold")).grid(row=0, column=0, rowspan=2, padx=(16, 10), pady=14)
        ctk.CTkLabel(shell, text="ULTRON // QUICK COMMAND", text_color=MUTED, font=ctk.CTkFont("Consolas", 8, "bold")).grid(row=0, column=1, sticky="w", pady=(12, 0))
        self.entry = ctk.CTkEntry(shell, height=36, fg_color=VOID, border_width=1, border_color=LINE, text_color=WHITE, placeholder_text="Ask ULTRON... / Pregúntale a ULTRON...", placeholder_text_color=MUTED, font=ctk.CTkFont("Consolas", 11))
        self.entry.grid(row=1, column=1, sticky="ew", pady=(2, 12))
        self.entry.bind("<Return>", lambda _e: self._send())
        self.entry.bind("<Escape>", lambda _e: self.withdraw())
        ctk.CTkButton(shell, text="EXECUTE", command=self._send, width=92, height=36, fg_color=RED_DARK, hover_color=RED, border_width=1, border_color=RED, text_color=WHITE, font=ctk.CTkFont("Consolas", 8, "bold")).grid(row=1, column=2, padx=(10, 6), pady=(2, 12))
        ctk.CTkButton(shell, text="×", command=self.withdraw, width=36, height=36, fg_color="transparent", hover_color=RED_DARK, text_color=WHITE, font=ctk.CTkFont("Segoe UI", 17, "bold")).grid(row=1, column=3, padx=(0, 10), pady=(2, 12))
        self.after(80, self.entry.focus_force)

    def _send(self) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self.withdraw()
        try:
            self.app._dispatch(text)
            self.app.lift()
        except Exception:
            pass


def install_overlay(UltronApp) -> None:
    if getattr(UltronApp, "_overlay_installed", False):
        return
    original_init = UltronApp.__init__

    def init_with_overlay(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._ultron_overlay = None

        def toggle_overlay() -> None:
            overlay = getattr(self, "_ultron_overlay", None)
            if overlay is None:
                overlay = UltronOverlay(self)
                self._ultron_overlay = overlay
                return
            try:
                if not overlay.winfo_exists():
                    self._ultron_overlay = UltronOverlay(self)
                    return
                if overlay.state() == "withdrawn":
                    overlay.deiconify()
                    overlay.lift()
                    overlay.entry.focus_force()
                else:
                    overlay.withdraw()
            except Exception:
                self._ultron_overlay = UltronOverlay(self)

        self.toggle_ultron_overlay = toggle_overlay
        self.bind("<Control-Shift-space>", lambda _event: toggle_overlay())

    UltronApp.__init__ = init_with_overlay
    UltronApp._overlay_installed = True
