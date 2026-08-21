from __future__ import annotations

import re
from dataclasses import dataclass

from ultron_core import AssistantReply, UltronBrain


@dataclass(frozen=True)
class Route:
    lane: str
    reason: str


def classify(text: str) -> Route:
    low = text.lower()
    if any(k in low for k in ("screen", "pantalla", "vision", "qué ves", "what do you see")):
        return Route("vision", "screen-related directive")
    if any(k in low for k in ("python", "code", "código", "debug", "error de código")):
        return Route("code", "programming request")
    if any(k in low for k in ("plan", "pasos", "strategy", "estrategia", "organiza")):
        return Route("planner", "multi-step request")
    if any(k in low for k in ("open ", "abre ", "window", "ventana", "volume", "volumen", "spotify", "discord")):
        return Route("local", "safe desktop action")
    if len(text.split()) > 45 or any(k in low for k in ("analyze", "analiza", "compare", "compara", "explain deeply", "explica a fondo")):
        return Route("reasoning", "complex reasoning request")
    return Route("chat", "general conversation")


def install_router_v2_patch() -> None:
    if getattr(UltronBrain, "_ultron_router_v2_installed", False):
        return
    original = UltronBrain.handle

    def handle(self: UltronBrain, raw: str) -> AssistantReply:
        route = classify(raw)
        self.memory.set_setting("ultron_last_route", route.lane)
        low = raw.lower().strip()
        if low in {"router status", "estado del router", "ai router", "router"}:
            provider = self.ai.provider.upper() if self.ai.available else "LOCAL"
            return AssistantReply(f"AI ROUTER v2 // PROVIDER {provider} // LAST LANE {route.lane.upper()}", "status")
        return original(self, raw)

    UltronBrain.handle = handle
    UltronBrain._ultron_router_v2_installed = True
