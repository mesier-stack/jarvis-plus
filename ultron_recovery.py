from __future__ import annotations

from collections import defaultdict

from jarvis_core import AssistantReply, JarvisBrain

_FAILURES = defaultdict(int)
_DISABLED = set()


def disabled_modules():
    return sorted(_DISABLED)


def install_recovery_patch() -> None:
    if getattr(JarvisBrain, "_ultron_recovery_installed", False):
        return
    original = JarvisBrain.handle

    def handle(self: JarvisBrain, raw: str):
        low = raw.lower().strip()
        if low in {"recovery status", "estado recovery", "recovery mode"}:
            disabled = ", ".join(disabled_modules()) or "none"
            return AssistantReply(f"RECOVERY MODE // DISABLED MODULES: {disabled}", "status")
        if low.startswith("recover ") or low.startswith("recupera "):
            name = low.split(" ", 1)[1].strip()
            _DISABLED.discard(name)
            _FAILURES[name] = 0
            return AssistantReply(f"Recovery counter reset for {name}.", "status")
        try:
            return original(self, raw)
        except Exception as exc:
            lane = self.memory.get_setting("ultron_last_route", "core")
            _FAILURES[lane] += 1
            if _FAILURES[lane] >= 3:
                _DISABLED.add(lane)
            return AssistantReply(
                f"{lane.upper()} NODE FAULT // request contained safely. Recovery mode kept the core online. {exc}",
                "error",
            )

    JarvisBrain.handle = handle
    JarvisBrain._ultron_recovery_installed = True
