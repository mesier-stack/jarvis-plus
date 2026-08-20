from __future__ import annotations

import os
import platform
import re

from jarvis_core import AssistantReply, JarvisBrain


HEALTH_PHRASES = {
    "ultron status", "ultron health", "self diagnostic", "self diagnostics",
    "diagnostico de ultron", "diagnóstico de ultron", "diagnostico ultron",
    "diagnóstico ultron", "revisa tus sistemas", "revisa tus modulos", "revisa tus módulos",
    "estado de ultron", "estado ultron",
}


def _check_module(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def _health_report() -> str:
    checks: list[tuple[str, bool, str]] = []

    openai = bool(os.getenv("OPENAI_API_KEY"))
    gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    ai_provider = "OpenAI" if openai else "Gemini" if gemini else "not configured"
    checks.append(("AI", openai or gemini, ai_provider))

    eleven = bool(os.getenv("ELEVENLABS_API_KEY"))
    local_voice = _check_module("pyttsx3")
    voice_detail = "ElevenLabs" if eleven else "local Windows TTS" if local_voice else "unavailable"
    checks.append(("Voice", eleven or local_voice, voice_detail))

    speech = _check_module("speech_recognition")
    audio = _check_module("sounddevice")
    checks.append(("Microphone stack", speech and audio, "SpeechRecognition + sounddevice" if speech and audio else "dependency missing"))

    pillow = _check_module("PIL")
    checks.append(("Screen capture", pillow, "Pillow ImageGrab" if pillow else "Pillow missing"))
    checks.append(("Screen vision", pillow and (openai or gemini), ai_provider if pillow and (openai or gemini) else "needs capture + AI"))

    psutil = _check_module("psutil")
    checks.append(("Telemetry", psutil, "psutil" if psutil else "limited"))

    ok_count = sum(1 for _name, ok, _detail in checks if ok)
    lines = [f"ULTRON SELF-DIAGNOSTIC // {ok_count}/{len(checks)} systems ready", f"Platform: {platform.system()} {platform.release()}"]
    for name, ok, detail in checks:
        lines.append(f"{'ONLINE' if ok else 'OFFLINE'} // {name}: {detail}")
    if ok_count < len(checks):
        lines.append("Offline modules do not disable the rest of ULTRON; they can be configured independently.")
    return "\n".join(lines)


def install_health_patch() -> None:
    if getattr(JarvisBrain, "_ultron_health_installed", False):
        return

    original_handle = JarvisBrain.handle

    def handle_with_health(self: JarvisBrain, raw: str) -> AssistantReply:
        normalized = re.sub(r"\s+", " ", raw.lower().strip(" .!?¿¡"))
        normalized_no_wake = re.sub(r"^(?:hey\s+)?ultron\s*[,;:\-]?\s*", "", normalized).strip()
        if normalized in HEALTH_PHRASES or normalized_no_wake in HEALTH_PHRASES or normalized_no_wake in {
            "status", "health", "self diagnostic", "self diagnostics", "diagnostico", "diagnóstico"
        }:
            self.memory.add_message("user", raw.strip())
            report = _health_report()
            self.memory.add_message("assistant", report)
            self.memory.record_event(raw.strip(), report, True)
            return AssistantReply(report, "status")
        return original_handle(self, raw)

    JarvisBrain.handle = handle_with_health
    JarvisBrain._ultron_health_installed = True
