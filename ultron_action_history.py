from __future__ import annotations

from collections import deque
from datetime import datetime

from ultron_core import UltronBrain

_HISTORY = deque(maxlen=80)


def _stamp(kind: str, text: str) -> None:
    _HISTORY.appendleft((datetime.now().strftime("%H:%M:%S"), kind, text[:160]))


def get_action_history(limit: int = 20):
    return list(_HISTORY)[:limit]


def install_action_history_patch() -> None:
    if getattr(UltronBrain, "_ultron_history_installed", False):
        return
    original = UltronBrain.handle

    def handle(self: UltronBrain, raw: str):
        _stamp("DIRECTIVE", raw)
        try:
            reply = original(self, raw)
            _stamp(getattr(reply, "kind", "REPLY").upper(), getattr(reply, "text", str(reply)))
            return reply
        except Exception as exc:
            _stamp("FAULT", str(exc))
            raise

    UltronBrain.handle = handle
    UltronBrain._ultron_history_installed = True
