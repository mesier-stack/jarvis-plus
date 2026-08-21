from __future__ import annotations

import time
from threading import Lock

from jarvis_core import JarvisBrain

_STATE = {"lane": "standby", "detail": "", "updated": time.time()}
_LOCK = Lock()


def set_activity(lane: str, detail: str = "") -> None:
    with _LOCK:
        _STATE.update(lane=lane, detail=detail[:120], updated=time.time())


def get_activity() -> dict:
    with _LOCK:
        return dict(_STATE)


def install_activity_patch() -> None:
    if getattr(JarvisBrain, "_ultron_activity_installed", False):
        return
    original = JarvisBrain.handle

    def handle(self: JarvisBrain, raw: str):
        lane = self.memory.get_setting("ultron_last_route", "cognition")
        set_activity(lane, raw)
        try:
            return original(self, raw)
        finally:
            set_activity("standby", "ready")

    JarvisBrain.handle = handle
    JarvisBrain._ultron_activity_installed = True
