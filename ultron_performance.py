from __future__ import annotations

from jarvis_core import AssistantReply, JarvisBrain


def install_performance_patch() -> None:
    if getattr(JarvisBrain, "_ultron_performance_installed", False):
        return
    original = JarvisBrain.handle

    def handle(self: JarvisBrain, raw: str):
        low = raw.lower().strip()
        if low in {"performance mode", "gaming mode", "modo rendimiento", "modo juego"}:
            self.memory.set_setting("ultron_performance_mode", "on")
            return AssistantReply("PERFORMANCE MODE ONLINE // reduced visual polling and background activity requested.", "setting")
        if low in {"performance off", "gaming off", "modo rendimiento off", "modo juego off"}:
            self.memory.set_setting("ultron_performance_mode", "off")
            return AssistantReply("PERFORMANCE MODE OFFLINE // full interface activity restored.", "setting")
        return original(self, raw)

    JarvisBrain.handle = handle
    JarvisBrain._ultron_performance_installed = True
