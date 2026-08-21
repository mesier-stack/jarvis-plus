from __future__ import annotations

import re
from jarvis_core import AssistantReply, JarvisBrain


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip(" .!?¿¡"))


def _looks_complex(text: str) -> bool:
    low = _norm(text)
    triggers = (
        "plan ", "make a plan", "haz un plan", "planifica", "organiza",
        "step by step", "paso a paso", "primero", "después", "despues",
    )
    return any(t in low for t in triggers) or len(text.split()) > 22


def _local_plan(text: str) -> str:
    spanish = any(x in _norm(text) for x in ("haz", "planifica", "organiza", "paso a paso", "después", "despues"))
    if spanish:
        return (
            "PLAN ULTRON\n"
            "1. Entender el objetivo exacto.\n"
            "2. Revisar qué información o app hace falta.\n"
            "3. Ejecutar primero solo acciones seguras/de lectura.\n"
            "4. Pedir confirmación antes de cualquier acción sensible.\n"
            "5. Verificar el resultado y ajustar si hace falta."
        )
    return (
        "ULTRON PLAN\n"
        "1. Clarify the exact objective.\n"
        "2. Inspect the information or app state needed.\n"
        "3. Perform safe/read-only steps first.\n"
        "4. Ask for confirmation before sensitive actions.\n"
        "5. Verify the outcome and adjust if needed."
    )


def install_planner_patch() -> None:
    if getattr(JarvisBrain, "_ultron_planner_installed", False):
        return
    original = JarvisBrain.handle

    def handle_planner(self: JarvisBrain, raw: str) -> AssistantReply:
        low = _norm(raw)
        explicit = any(x in low for x in ("make a plan", "haz un plan", "planifica", "organiza esto", "plan this"))
        if explicit:
            if self.ai.available:
                try:
                    history = self.memory.recent_messages() + [{"role": "user", "content": raw}]
                    answer = self.ai.answer(
                        "Create a short actionable plan. Put safe/read-only steps first and clearly mark any step that would require user confirmation.",
                        history,
                        self.memory.relevant_memories(raw),
                        self.memory.get_setting("voice_profile", "cinematic"),
                    )
                    return AssistantReply(answer, "plan")
                except Exception:
                    pass
            return AssistantReply(_local_plan(raw), "plan")
        return original(self, raw)

    JarvisBrain.handle = handle_planner
    JarvisBrain._ultron_planner_installed = True
