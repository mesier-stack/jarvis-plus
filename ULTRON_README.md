# ULTRON v0.1

ULTRON is the next-generation interface built on top of the stable local capabilities from JARVIS+.

## Included now

- New red/black ULTRON desktop interface
- Animated central adaptive core
- Text command console
- Reuses existing AI provider configuration
- Reuses existing local memory database
- Reuses existing Windows-safe actions
- Reuses existing screenshot support
- Reuses existing ElevenLabs/local voice engine
- Live CPU, RAM and storage telemetry
- Memory-bank counter
- Voice on/off switch
- Fullscreen mode
- Quick actions for system scan, screenshot, memory and notes

## Safety model

ULTRON v0.1 intentionally inherits the existing safe action layer instead of adding unrestricted shell execution. Destructive or sensitive capabilities should remain permission-gated.

## Run on Windows

Double-click:

`run_ultron.bat`

Or from a terminal:

```powershell
python ultron_main.py
```

## Architecture direction

The next versions should split the system into independent modules:

1. `core` - reasoning/router
2. `memory` - persistent local context
3. `voice` - speech input/output
4. `vision` - screenshots/camera understanding
5. `actions` - permission-gated PC control
6. `network` - web research/connectors
7. `ui` - ULTRON command interface
8. `security` - confirmation and permission policy

## Planned milestones

### v0.2 - Voice Command Loop
Always-ready push-to-talk input, visible listening state and interruption support.

### v0.3 - Vision
Screen capture analysis and contextual questions about what is visible.

### v0.4 - Modular Actions
Plugin-style Windows actions with explicit risk levels and confirmation gates.

### v0.5 - Memory Upgrade
Project-specific memories, searchable session history and configurable retention.

### v1.0 - ULTRON Core
Unified voice, vision, memory, actions and web intelligence behind the ULTRON interface.
