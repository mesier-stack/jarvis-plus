from __future__ import annotations

import re

from ultron_core import AssistantReply, UltronBrain


def install_visual_action_patch() -> None:
    if getattr(UltronBrain, "_ultron_visual_action_installed", False):
        return
    original = UltronBrain.handle

    def handle(self: UltronBrain, raw: str):
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

    UltronBrain.handle = handle
    UltronBrain._ultron_visual_action_installed = True
