from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    safety: str = "standard"


SKILLS = {
    "vision": Skill("VISION", "Analyze the screen only when requested.", "privacy"),
    "windows": Skill("WINDOWS", "Inspect and manage the active window.", "permission"),
    "files": Skill("FILES", "Find user files in common folders.", "privacy"),
    "memory": Skill("MEMORY", "Store and retrieve categorized memories.", "privacy"),
    "planner": Skill("PLANNER", "Break complex directives into visible steps."),
    "voice": Skill("VOICE", "Bilingual speech input and spoken responses.", "microphone"),
    "watch": Skill("WATCH", "Observe explicitly selected local conditions.", "privacy"),
    "diagnostics": Skill("DIAGNOSTICS", "Report ULTRON and system health."),
}


def skill_summary() -> str:
    return "\n".join(f"{s.name:<12} // {s.description}" for s in SKILLS.values())
