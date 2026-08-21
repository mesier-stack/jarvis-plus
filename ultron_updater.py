from __future__ import annotations

import json
import urllib.request
from jarvis_core import AssistantReply, JarvisBrain

REPO_API = "https://api.github.com/repos/mesier-stack/jarvis-plus/commits/main"


def _latest_sha() -> str:
    req = urllib.request.Request(REPO_API, headers={"User-Agent": "ULTRON-Updater"})
    with urllib.request.urlopen(req, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data.get("sha", ""))


def install_update_check_patch() -> None:
    if getattr(JarvisBrain, "_ultron_updater_installed", False):
        return
    original = JarvisBrain.handle

    def wrapped(self: JarvisBrain, raw: str) -> AssistantReply:
        low = raw.lower().strip(" .!?¿¡")
        if low in {"check for updates", "check updates", "buscar actualizaciones", "revisa actualizaciones"}:
            try:
                sha = _latest_sha()
                if not sha:
                    raise RuntimeError("No commit SHA returned")
                previous = self.memory.get_setting("ultron_last_seen_commit", "")
                self.memory.set_setting("ultron_last_seen_commit", sha)
                if previous and previous != sha:
                    return AssistantReply(
                        "A newer repository revision is available. I will not install it automatically. Pull the latest repo when you choose.",
                        "status",
                    )
                return AssistantReply("Repository check complete. No unseen revision detected.", "status")
            except Exception as exc:
                return AssistantReply(f"Update check failed: {exc}", "error")
        return original(self, raw)

    JarvisBrain.handle = wrapped
    JarvisBrain._ultron_updater_installed = True
