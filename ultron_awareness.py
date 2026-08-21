from __future__ import annotations

import os
import re

from ultron_core import AssistantReply, UltronBrain


WINDOW_PATTERNS = {
    "what window is open",
    "what app am i using",
    "what app is open",
    "active window",
    "active app",
    "que ventana tengo abierta",
    "qué ventana tengo abierta",
    "que app estoy usando",
    "qué app estoy usando",
    "ventana activa",
    "aplicacion activa",
    "aplicación activa",
}


def _active_window() -> tuple[str, str]:
    if os.name != "nt":
        return "Unknown", "Active-window awareness is currently available on Windows only."

    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return "Unknown", "No foreground window detected."

        length = user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        title = buffer.value.strip() or "Untitled window"

        process_id = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
        process_name = "Unknown process"
        try:
            import psutil

            process_name = psutil.Process(process_id.value).name()
        except Exception:
            pass
        return process_name, title
    except Exception as exc:
        return "Unknown", f"Active-window check failed: {exc}"


def install_awareness_patch() -> None:
    if getattr(UltronBrain, "_ultron_awareness_installed", False):
        return

    original_handle = UltronBrain.handle

    def handle_with_awareness(self: UltronBrain, raw: str) -> AssistantReply:
        low = re.sub(r"\s+", " ", raw.lower().strip(" .!?¿¡"))
        if low in WINDOW_PATTERNS:
            process, title = _active_window()
            if process == "Unknown" and title.startswith("Active-window"):
                return AssistantReply(title, "error")
            return AssistantReply(
                f"Active application: {process}\nWindow: {title}",
                "awareness",
            )
        return original_handle(self, raw)

    UltronBrain.handle = handle_with_awareness
    UltronBrain._ultron_awareness_installed = True
