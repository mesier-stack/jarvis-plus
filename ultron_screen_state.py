from __future__ import annotations

import hashlib
import time

from ultron_core import AssistantReply, UltronBrain

_LAST = {"hash": None, "time": 0.0}


def _screen_fingerprint() -> str:
    from PIL import ImageGrab
    image = ImageGrab.grab(all_screens=True).convert("L")
    image.thumbnail((160, 90))
    return hashlib.sha256(image.tobytes()).hexdigest()


def screen_changed(update: bool = True) -> tuple[bool | None, float]:
    now = time.time()
    current = _screen_fingerprint()
    previous = _LAST["hash"]
    age = now - _LAST["time"] if _LAST["time"] else 0.0
    changed = None if previous is None else current != previous
    if update:
        _LAST["hash"] = current
        _LAST["time"] = now
    return changed, age


def install_screen_state_patch() -> None:
    if getattr(UltronBrain, "_ultron_screen_state_installed", False):
        return
    original = UltronBrain.handle

    def handle(self: UltronBrain, raw: str):
        low = raw.lower().strip(" .!?")
        if low in {"screen changed", "did my screen change", "cambio la pantalla", "cambió la pantalla", "pantalla cambio", "pantalla cambió"}:
            try:
                changed, age = screen_changed(update=True)
                if changed is None:
                    return AssistantReply("SCREEN STATE BASELINE CREATED // ask again after the screen changes.", "status")
                return AssistantReply(
                    f"SCREEN STATE // {'CHANGED' if changed else 'UNCHANGED'} // previous baseline age {age:.1f}s",
                    "status",
                )
            except Exception as exc:
                return AssistantReply(f"SCREEN STATE NODE FAULT // {exc}", "error")
        return original(self, raw)

    UltronBrain.handle = handle
    UltronBrain._ultron_screen_state_installed = True
