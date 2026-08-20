from __future__ import annotations

import base64
import os
import re
import tempfile
from pathlib import Path

from jarvis_core import AssistantReply, JarvisBrain


VISION_PATTERNS = (
    "mira mi pantalla", "mira la pantalla", "analiza mi pantalla", "analiza la pantalla",
    "que ves en mi pantalla", "qué ves en mi pantalla", "revisa mi pantalla",
    "diagnostica mi pantalla", "diagnostica la pantalla", "encuentra el error en mi pantalla",
    "que error ves", "qué error ves", "screen vision", "look at my screen",
    "analyze my screen", "analyse my screen", "what do you see on my screen",
    "diagnose my screen", "find the error on my screen",
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip(" .!?¿¡"))


def _is_vision_request(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern in normalized for pattern in VISION_PATTERNS)


def _vision_mode(text: str) -> str:
    low = _normalize(text)
    if any(word in low for word in ("error", "falla", "fallo", "problema", "diagnost", "fix", "wrong")):
        return "diagnostic"
    if any(word in low for word in ("resume", "resumen", "summary", "qué hay", "que hay")):
        return "summary"
    if any(word in low for word in ("qué hago", "que hago", "what should i do", "next step", "siguiente paso")):
        return "guidance"
    return "general"


def _capture_screen() -> Path:
    from PIL import ImageGrab

    folder = Path.home() / "Pictures" / "ULTRON"
    folder.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix="ultron-vision-", suffix=".png", dir=folder)
    os.close(descriptor)
    path = Path(temp_name)

    image = ImageGrab.grab(all_screens=True)
    max_width = 1800
    if image.width > max_width:
        height = int(image.height * (max_width / image.width))
        image = image.resize((max_width, height))
    image.save(path, format="PNG", optimize=True)
    return path


def _vision_prompt(user_text: str) -> str:
    mode = _vision_mode(user_text)
    mode_instruction = {
        "diagnostic": (
            "This is a troubleshooting request. Identify the most likely visible problem first. "
            "Then give 2-5 concrete steps in the safest order. Distinguish clearly between what is visible "
            "and what is only a hypothesis."
        ),
        "summary": "Summarize the important visible content and ignore decorative or irrelevant UI.",
        "guidance": (
            "Focus on the user's next action. Explain exactly where to look or what control to use, "
            "without pretending you clicked anything."
        ),
        "general": "Describe the important visible elements, then answer the user's request directly.",
    }[mode]

    return (
        "You are ULTRON, a precise private desktop assistant analyzing a screenshot from the user's own PC. "
        "Reply in the same language as the user. Only use information actually visible in the screenshot. "
        "Never infer passwords, hidden values, identity, private messages outside what is visibly shown, or secrets. "
        "If a credential/token/API key is visible, do not repeat it; say that sensitive information is visible instead. "
        "Never claim you clicked, changed, installed, sent, deleted, or executed anything. "
        f"{mode_instruction}\n\nUser request: {user_text}"
    )


def _analyze_openai(path: Path, prompt: str) -> str:
    from openai import OpenAI

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_VISION_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4.1-mini"
    response = client.responses.create(
        model=model,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/png;base64,{encoded}", "detail": "auto"},
            ],
        }],
        max_output_tokens=850,
    )
    return response.output_text.strip()


def _analyze_gemini(path: Path, prompt: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    model = os.getenv("GEMINI_VISION_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
    image = types.Part.from_bytes(data=path.read_bytes(), mime_type="image/png")
    response = client.models.generate_content(model=model, contents=[image, prompt])
    return (response.text or "").strip()


def analyze_screen(user_text: str) -> str:
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if not (has_openai or has_gemini):
        return (
            "La visión de pantalla está instalada, pero falta conectar una IA compatible con imágenes. "
            "Configura OpenAI o Gemini y vuelve a pedirme que mire la pantalla."
            if any(ch in user_text.lower() for ch in "áéíóúñ") or "pantalla" in user_text.lower()
            else "Screen vision is installed, but no image-capable AI provider is configured. Configure OpenAI or Gemini first."
        )

    path = _capture_screen()
    prompt = _vision_prompt(user_text)
    errors: list[str] = []
    try:
        # Prefer the provider already selected by environment, but fail over if both keys exist.
        if has_openai:
            try:
                answer = _analyze_openai(path, prompt)
                if answer:
                    return answer
            except Exception as exc:
                errors.append(f"OpenAI: {exc}")
        if has_gemini:
            try:
                answer = _analyze_gemini(path, prompt)
                if answer:
                    return answer
            except Exception as exc:
                errors.append(f"Gemini: {exc}")
        detail = " | ".join(errors)[:500] or "No provider returned an answer."
        return f"Capturé la pantalla, pero el análisis visual falló: {detail}"
    except Exception as exc:
        return f"No pude completar el análisis de pantalla: {exc}"
    finally:
        try:
            path.unlink(missing_ok=True)
        except Exception:
            pass


def install_vision_patch() -> None:
    """Install screen vision only for ULTRON entrypoints."""
    if getattr(JarvisBrain, "_ultron_vision_installed", False):
        return

    original_handle = JarvisBrain.handle

    def handle_with_vision(self: JarvisBrain, raw: str) -> AssistantReply:
        if _is_vision_request(raw):
            self.memory.add_message("user", raw.strip())
            answer = analyze_screen(raw)
            self.memory.add_message("assistant", answer)
            success = not answer.lower().startswith(("no pude", "screen vision is installed", "la visión de pantalla"))
            self.memory.record_event(raw.strip(), answer, success)
            return AssistantReply(text=answer, kind="vision" if success else "error")
        return original_handle(self, raw)

    JarvisBrain.handle = handle_with_vision
    JarvisBrain._ultron_vision_installed = True
