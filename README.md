# ULTRON

ULTRON is a private Windows desktop intelligence with bilingual English/Spanish conversation, NVIDIA Nemotron support, screen vision, local memory, voice, safe Windows controls, permission gates, telemetry, an animated neural-brain interface, overlay controls, recovery mode, performance mode, watch mode, and self-updates.

## Run

Double-click `run_ultron.bat`, or run:

```powershell
python ultron_entry.py
```

## AI providers

ULTRON can use NVIDIA NIM, OpenAI, or Gemini. Keep API keys in Windows environment variables, never in source code:

```powershell
setx NVIDIA_API_KEY "your-key"
setx OPENAI_API_KEY "your-key"
setx GEMINI_API_KEY "your-key"
```

NVIDIA Nemotron is used as a reasoning provider when `NVIDIA_API_KEY` is available. Vision can use a compatible multimodal provider when configured.

## Voice

ULTRON supports ElevenLabs, OpenAI/Gemini speech where available, and a local Windows fallback.

```powershell
setx ELEVENLABS_API_KEY "your-key"
setx ELEVENLABS_VOICE_ID "your-voice-id"
```

## Useful commands

- `Ultron, revisa tus sistemas`
- `Ultron, mira mi pantalla`
- `Ultron, router status`
- `Ultron, focus mode`
- `Ultron, check for updates`
- `Ultron, update ultron`
- `Ultron, open Spotify`
- `Ultron, what app am I using?`
- `Ultron, find file ciencias`
- `Ultron, performance mode`

## Security model

ULTRON separates reasoning from local actions. Protected or destructive actions are permission-gated. Screen analysis is on-demand, temporary screen context is session-only, and API keys are read from the Windows user environment rather than committed to the repository.

## Architecture

The runtime is organized into `ultron_*` modules for identity, AI routing, NVIDIA, vision, bilingual speech, awareness, memory, files, planner, permissions, Windows control, recovery, performance, skills, updater, overlay, command center, and the neural-brain UI.

## Updating

Once the current updater is installed, say or type:

```text
check for updates
update ultron
```

The updater downloads the current main branch, refreshes dependencies, preserves Windows environment API keys, and reopens ULTRON.
