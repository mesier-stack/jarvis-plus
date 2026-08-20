from __future__ import annotations

import re
import time
from pathlib import Path

from jarvis_core import AssistantReply, JarvisBrain


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip(" .!?¿¡"))


def _focus_status(memory) -> bool:
    return memory.get_setting("ultron_focus", "off") == "on"


def install_focus_patch() -> None:
    if getattr(JarvisBrain, "_ultron_focus_installed", False):
        return

    original_handle = JarvisBrain.handle

    def handle_with_focus(self: JarvisBrain, raw: str) -> AssistantReply:
        low = _clean(raw)

        if low in {"focus mode", "modo enfoque", "ultron focus", "activar modo enfoque"}:
            self.memory.set_setting("ultron_focus", "on")
            return AssistantReply(
                "Focus mode online. I will keep responses shorter and prioritize the next useful action.",
                "setting",
            )

        if low in {"focus off", "disable focus", "desactivar modo enfoque", "modo enfoque off"}:
            self.memory.set_setting("ultron_focus", "off")
            return AssistantReply("Focus mode offline. Normal response depth restored.", "setting")

        if low in {"quick status", "estado rapido", "estado rápido"}:
            provider = self.ai.provider.upper() if self.ai.available else "LOCAL"
            focus = "ON" if _focus_status(self.memory) else "OFF"
            return AssistantReply(f"CORE ONLINE · AI {provider} · FOCUS {focus}", "status")

        reply = original_handle(self, raw)
        if _focus_status(self.memory) and reply.kind not in {"memory", "learning", "error"}:
            lines = [line.strip() for line in reply.text.splitlines() if line.strip()]
            if len(lines) > 3:
                reply.text = "\n".join(lines[:3])
        return reply

    JarvisBrain.handle = handle_with_focus
    JarvisBrain._ultron_focus_installed = True
