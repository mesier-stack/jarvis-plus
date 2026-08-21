from __future__ import annotations

from jarvis_core import AssistantReply, JarvisBrain
from ultron_skills import SKILLS, skill_summary


def install_skills_v2_patch() -> None:
    if getattr(JarvisBrain, "_ultron_skills_v2_installed", False):
        return
    original = JarvisBrain.handle

    def handle(self: JarvisBrain, raw: str):
        low = raw.lower().strip(" .!?")
        if low in {"skills", "skill registry", "habilidades", "modulos", "módulos"}:
            lines = []
            for key, skill in SKILLS.items():
                enabled = self.memory.get_setting(f"skill_{key}", "on") != "off"
                lines.append(f"{'ONLINE' if enabled else 'OFFLINE':<7} // {skill.name:<12} // {skill.description}")
            return AssistantReply("SKILL ENGINE v2\n" + "\n".join(lines), "status")
        for prefix, enabled in (("disable skill ", False), ("desactiva skill ", False), ("enable skill ", True), ("activa skill ", True)):
            if low.startswith(prefix):
                name = low[len(prefix):].strip()
                if name not in SKILLS:
                    return AssistantReply(f"Unknown skill: {name}", "error")
                self.memory.set_setting(f"skill_{name}", "on" if enabled else "off")
                return AssistantReply(f"{SKILLS[name].name} // {'ONLINE' if enabled else 'OFFLINE'}", "setting")
        return original(self, raw)

    JarvisBrain.handle = handle
    JarvisBrain._ultron_skills_v2_installed = True
