# JARVIS+

A native Windows learning assistant with a futuristic desktop HUD, local memory,
voice input/output, safe PC controls, reminders, notes, system telemetry, a safe
learning engine, and an optional OpenAI-powered conversational brain and natural voice.

Version 3.3 uses a cinematic fullscreen reactor HUD. Press `Escape` to leave fullscreen
or `F11` to toggle it. The interface includes animated targeting rings, a voice
waveform, system telemetry, learning status, quick directives, and a compact comms log.

## Fast start on Windows

1. Install **Python 3.11 or newer** from python.org and enable “Add Python to PATH”.
2. Double-click `run_jarvis.bat`.
3. The first launch installs its dependencies; later launches are immediate.

The microphone uses PyAudio when available and automatically falls back to
SoundDevice on Windows, avoiding the most common voice-installation failure.

## Automatic updates

Version 3.2 includes the automatic-update client. JARVIS+ checks
for a newer signed-off package at launch and also provides an **UPDATE** button.
It downloads over HTTPS, verifies the package SHA-256 checksum, rejects unexpected
files, closes safely, replaces only application files, and restarts itself.

Updates never replace `.env`, `.venv`, or the private database under `%APPDATA%`.
An update is never installed until you approve the visible confirmation.

## Activate an AI brain (optional)

JARVIS+ works without an API key for all local commands. For natural conversation,
create an OpenAI API key and run this once in PowerShell:

```powershell
setx OPENAI_API_KEY "your-key"
setx OPENAI_MODEL "gpt-5.6"
```

Close and reopen JARVIS+ afterward. Keep the key private and never put it in the
source code or send it in chat. API use can cost money according to your account.
When configured, both the fluent chat brain and natural AI-generated voice activate.

Alternatively, use a Google AI Studio key for Gemini chat and Gemini natural voice:

```powershell
setx GEMINI_API_KEY "your-google-ai-studio-key"
```

JARVIS+ automatically detects the provider. If both keys exist, OpenAI has priority.
The easiest setup is the **AI SETUP** button inside JARVIS+: paste the key into the
private masked window. On Windows it is saved to your user environment and activated
immediately. Never paste an API key into chat.

## Things to say or type

- `Jarvis, open calculator` / `abre calculadora`
- `open the calculator` / `abre la calculadora`
- `PC status` / `estado del PC`
- `calculate (45 * 8) / 3`
- `note buy the Ryzen` / `anota llamar al cliente`
- `show my notes` / `mis notas`
- `remind me in 10 minutes to study`
- `remind me to test Jarvis in 1 minute`
- `teach launch numbers => open calculator`
- `wrong, use open calculator` (corrects the previous command)
- `learning report`
- `forget launch numbers`
- `speak Spanish`, `speak English`, or `bilingual mode`
- `search RTX 5060 Chile`
- `take a screenshot`
- `lock PC`, `restart PC`, or `shutdown`

Shutdown, restart, and locking always require a visible confirmation. AI responses
cannot directly execute operating-system actions.

## Safe learning system

JARVIS+ records misunderstood attempts locally and learns phrase-to-command
corrections you explicitly provide. Learned phrases survive restarts, tolerate
small wording differences, and can be reviewed with `learning report` or removed
with `forget ...`. Learning never creates shell commands or bypasses the app
allowlist: a learned shutdown still requires the same visible confirmation.

## Wake word and voice

Use **LISTEN** for one command, or enable **WAKE WORD** and begin with “Jarvis”.
Voice recognition uses the microphone and Google Speech Recognition; text commands
and local memory continue to work when voice or internet is unavailable.

With an OpenAI key, JARVIS+ uses `gpt-4o-mini-tts` and the `cedar` voice. With a
Google AI Studio key, it uses Gemini TTS and the mature `Gacrux` voice. Both use an
original low-register, measured British-style delivery and are AI-generated,
not human recordings. If cloud speech fails, the app falls back to an installed
Windows voice. Without either API key, command chat works locally, but open-ended
conversation is limited because no language model is available.

Fast voice is now the default: it begins with a brisker delivery and only reads the
essential first part of very long answers while leaving the complete answer visible.
Say or type `voice faster`, `voice normal`, or `voice slower` to change the persistent
speed. Use `voice test` to preview it.

## Build a standalone EXE

Double-click `build_exe.bat`. The packaged program appears under `dist\JARVIS+\`.
Move that complete folder anywhere on the same PC. The database remains private in:

```text
%APPDATA%\JarvisPlus\jarvis.db
```

## Architecture and security

- `main.py`: native Tkinter HUD, voice controls, animation, and confirmations.
- `jarvis_core.py`: intent engine, local memory, AI client, and allowlisted actions.
- `updater.py`: checksum-verified updater that preserves private data and settings.
- No arbitrary shell command from chat is executed.
- Destructive power commands are never automatic.
- Notes, reminders, and conversation memory stay in a local SQLite database.
- The API key is read only from the Windows environment.

This is the first complete release foundation: features can be added by extending
`JarvisBrain._local_command` and the allowlist in `SystemActions.APP_COMMANDS`.
