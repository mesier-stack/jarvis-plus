from __future__ import annotations

import re

from jarvis_core import AssistantReply, JarvisBrain, VoiceEngine


SPANISH_HINTS = {
    "el", "la", "los", "las", "que", "qué", "como", "cómo", "donde", "dónde", "abre",
    "pantalla", "haz", "hace", "quiero", "puedes", "gracias", "hola", "ahora", "esto", "esa",
}
ENGLISH_HINTS = {
    "the", "what", "where", "how", "open", "screen", "please", "can", "you", "thanks", "hello",
    "now", "this", "that", "show", "tell", "look", "check",
}


def _words(text: str) -> list[str]:
    return re.findall(r"[a-záéíóúñü]+", text.lower())


def _score(text: str, lang: str) -> float:
    words = _words(text)
    if not words:
        return -10.0
    hints = SPANISH_HINTS if lang == "es" else ENGLISH_HINTS
    score = sum(1.0 for word in words if word in hints)
    if lang == "es":
        score += sum(0.6 for ch in text.lower() if ch in "áéíóúñ¿¡")
    else:
        score += sum(0.3 for word in words if word in {"i", "i'm", "don't", "isn't", "it's"})
    score += min(len(text), 80) / 200.0
    return score


def _looks_spanish(text: str) -> bool:
    return _score(text, "es") > _score(text, "en")


def install_bilingual_patch() -> None:
    if getattr(VoiceEngine, "_ultron_bilingual_installed", False):
        return

    original_listen = VoiceEngine.listen_once

    @staticmethod
    def bilingual_listen_once(timeout: int = 5, phrase_time_limit: int = 9, language: str = "auto") -> tuple[bool, str]:
        if language != "auto":
            return original_listen(timeout=timeout, phrase_time_limit=phrase_time_limit, language=language)

        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.25)
                    audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except (AttributeError, OSError):
                import sounddevice as sd

                sample_rate = 16_000
                recording = sd.rec(
                    int(phrase_time_limit * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype="int16",
                )
                sd.wait()
                audio = sr.AudioData(recording.tobytes(), sample_rate, 2)

            candidates: list[tuple[float, str]] = []
            for recognition_language, tag in (("es-CL", "es"), ("en-US", "en")):
                try:
                    text = recognizer.recognize_google(audio, language=recognition_language).strip()
                    if text:
                        candidates.append((_score(text, tag), text))
                except sr.UnknownValueError:
                    pass
                except Exception:
                    pass

            if not candidates:
                return False, "No pude entenderte / I couldn't understand that."
            candidates.sort(key=lambda item: item[0], reverse=True)
            return True, candidates[0][1]
        except Exception as exc:
            return False, f"Microphone unavailable: {exc}"

    VoiceEngine.listen_once = bilingual_listen_once
    VoiceEngine._ultron_bilingual_installed = True

    original_handle = JarvisBrain.handle

    def handle_bilingual(self: JarvisBrain, raw: str) -> AssistantReply:
        low = raw.lower().strip(" .!?¿¡")
        if low in {
            "bilingual mode", "modo bilingüe", "modo bilingue", "english and spanish",
            "inglés y español", "ingles y español", "spanish and english",
        }:
            self.memory.set_setting("voice_language", "auto")
            return AssistantReply(
                "Bilingual mode online. I can listen, read, and reply in English, Spanish, or a natural mix of both.",
                "setting",
                voice_language="auto",
            )
        return original_handle(self, raw)

    JarvisBrain.handle = handle_bilingual
