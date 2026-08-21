from __future__ import annotations

import re
from ultron_core import AssistantReply, UltronBrain

PERMISSIONS = {
    "close_window": "ask",
    "power": "ask",
    "open_app": "allow",
    "screen_vision": "allow",
    "file_search": "allow",
}


def _key(action: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", action.lower().strip()).strip("_")


def _get(memory, action: str) -> str:
    default = PERMISSIONS.get(action, "ask")
    return memory.get_setting(f"ultron_permission_{action}", default)


def _set(memory, action: str, value: str) -> None:
    memory.set_setting(f"ultron_permission_{action}", value)


def install_permission_patch() -> None:
    if getattr(UltronBrain, "_ultron_permissions_installed", False):
        return
    original = UltronBrain.handle

    def wrapped(self: UltronBrain, raw: str) -> AssistantReply:
        text = raw.strip()
        low = text.lower().strip(" .!?¿¡")

        if low in {"permission center", "permissions", "centro de permisos", "permisos"}:
            rows = [f"{name}: {_get(self.memory, name).upper()}" for name in PERMISSIONS]
            return AssistantReply("ULTRON Permission Center\n" + "\n".join(rows), "setting")

        match = re.match(
            r"^(?:permission|permiso)\s+([a-z_ ]+)\s+(allow|ask|deny|permitir|preguntar|bloquear)$",
            low,
        )
        if match:
            action = _key(match.group(1))
            value = match.group(2)
            value = {"permitir": "allow", "preguntar": "ask", "bloquear": "deny"}.get(value, value)
            if action not in PERMISSIONS:
                return AssistantReply(f"Unknown permission: {action}", "error")
            _set(self.memory, action, value)
            return AssistantReply(f"Permission {action} set to {value.upper()}.", "setting")

        return original(self, raw)

    UltronBrain.handle = wrapped
    UltronBrain._ultron_permissions_installed = True
