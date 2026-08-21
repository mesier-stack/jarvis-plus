from __future__ import annotations

import ctypes
import re
from ctypes import wintypes

from jarvis_core import AssistantReply, JarvisBrain


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip(" .!?¿¡"))


def _active_hwnd():
    return ctypes.windll.user32.GetForegroundWindow() if hasattr(ctypes, "windll") else 0


def _show(hwnd: int, code: int) -> bool:
    if not hwnd:
        return False
    return bool(ctypes.windll.user32.ShowWindow(hwnd, code) or True)


def _move(hwnd: int, x: int, y: int, w: int, h: int) -> bool:
    if not hwnd:
        return False
    return bool(ctypes.windll.user32.MoveWindow(hwnd, x, y, w, h, True))


def _screen_size():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def install_window_control_patch() -> None:
    if getattr(JarvisBrain, "_ultron_window_control_installed", False):
        return
    original = JarvisBrain.handle

    def handle_windows(self: JarvisBrain, raw: str) -> AssistantReply:
        low = _norm(raw)
        if not hasattr(ctypes, "windll"):
            return original(self, raw)

        hwnd = _active_hwnd()
        if low in {"minimize this window", "minimize window", "minimiza esta ventana", "minimiza la ventana"}:
            _show(hwnd, 6)
            return AssistantReply("Window minimized.", "action")
        if low in {"maximize this window", "maximize window", "maximiza esta ventana", "maximiza la ventana"}:
            _show(hwnd, 3)
            return AssistantReply("Window maximized.", "action")
        if low in {"restore this window", "restore window", "restaura esta ventana", "restaura la ventana"}:
            _show(hwnd, 9)
            return AssistantReply("Window restored.", "action")
        if low in {"put this window left", "snap left", "pon esta ventana a la izquierda", "ventana a la izquierda"}:
            sw, sh = _screen_size()
            _move(hwnd, 0, 0, sw // 2, sh)
            return AssistantReply("Window moved to the left half.", "action")
        if low in {"put this window right", "snap right", "pon esta ventana a la derecha", "ventana a la derecha"}:
            sw, sh = _screen_size()
            _move(hwnd, sw // 2, 0, sw // 2, sh)
            return AssistantReply("Window moved to the right half.", "action")
        if low in {"close this window", "close window", "cierra esta ventana", "cierra la ventana"}:
            return AssistantReply(
                "Closing the active window requires confirmation.",
                "action",
                requires_confirmation="close active window",
            )
        if low in {"confirm close active window", "confirm close window"}:
            if hwnd:
                ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
                return AssistantReply("Active window close command sent.", "action")
            return AssistantReply("No active window found.", "error")

        return original(self, raw)

    JarvisBrain.handle = handle_windows
    JarvisBrain._ultron_window_control_installed = True
