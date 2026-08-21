from __future__ import annotations

import re

from jarvis_core import AssistantReply, JarvisBrain


def install_visual_action_patch() -> None:
    if getattr(JarvisBrain, "_ultron_visual_action_installed", False):
        return
    original = JarvisBrain.handle

    def handle(self: JarvisBrain, raw: str):
        low = raw.lower().strip()
        match = re.match(r"^(?:click|press|pulsa|haz click en|clic en)\s+(.+)$", low)
        if match:
            target = match.group(1).strip()
            permission = self.memory.get_setting("permission_visual_click", "ask")
            if permission == "deny":
                return AssistantReply("VISUAL ACTION BLOCKED // permission is DENY.", "error")
            if permission == "allow":
                return AssistantReply(
                    f"VISUAL ACTION READY // I identified the requested target as '{target}'. Automatic clicking is not enabled yet; use screen vision to verify the target first.",
                    "vision",
                )
            return AssistantReply(
                f"VISUAL ACTION PLAN // target: {target}. I will require a fresh screen scan and explicit confirmation before any future mouse action.",
                "confirm",
                requires_confirmation="visual_click",
            )
        return original(self, raw)

    JarvisBrain.handle = handle
    JarvisBrain._ultron_visual_action_installed = True
