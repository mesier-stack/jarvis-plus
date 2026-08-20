from __future__ import annotations

import base64
import os
import re
import tempfile
from pathlib import Path

from jarvis_core import AssistantReply, JarvisBrain


VISION_PATTERNS = (
    "mira mi pantalla",
    "mira la pantalla",
    "analiza mi pantalla",
    "analiza la pantalla",
    "que ves en mi pantalla",
    "qué ves en mi pantalla",
    "revisa mi pantalla",
    "screen vision",
    "look at my screen",
    "analyze my screen",
    "analyse my screen",
    "what do you see on my screen",
)


def _is_vision_request(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.lower().strip(" .!?¿¡"))
    return any(pattern in normalized for pattern in VISION_PATTERNS)


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
    return (
        "You are ULTRON, a precise desktop assistant. Analyze this screenshot from the user's own PC. "
        "Reply in the same language as the user. Focus only on what is visibly on screen, likely errors, "
        "important UI state, and concrete next steps. Never claim you clicked, changed, or executed anything. "
        "Do not infer passwords, hidden data, identities, or anything not visible. If the request is broad, "
        "briefly describe the important visible elements first, then explain what the user can do next.\n\n"
        f"User request: {user_text}"
    )


def _analyze_openai(path: Path, prompt: str) -> str:
    from openai import OpenAI

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_VISION_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4.1-mini"
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{encoded}",
                        "detail": "auto",
                    },
                ],
            }
        ],
        max_output_tokens=700,
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
            "Screen vision is installed, but no vision-capable AI key is configured. "
            "Configure OpenAI or Gemini first, then ask me to look at the screen again."
        )

    path = _capture_screen()
    prompt = _vision_prompt(user_text)
    try:
        if has_openai:
            return _analyze_openai(path, prompt)
        return _analyze_gemini(path, prompt)
    except Exception as exc:
        return f"I captured the screen, but vision analysis failed: {exc}"
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
            return AssistantReply(text=answer, kind="vision")
        return original_handle(self, raw)

    JarvisBrain.handle = handle_with_vision
    JarvisBrain._ultron_vision_installed = True
