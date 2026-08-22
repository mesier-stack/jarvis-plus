from __future__ import annotations

import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import ultron_entry
import ultron_main

app=ultron_main.UltronApp()
app.withdraw()
app.update_idletasks()
app.update()

commands=[
    'context status',
    'learning status',
    'evolution status',
    'evolution fitness',
    'goals',
    'web studio status',
    'dependency check',
    'current profile',
    'what do you remember',
]

failed=[]
for command in commands:
    try:
        reply=app.brain.handle(command)
        text=getattr(reply,'text',None)
        if not isinstance(text,str) or not text.strip():
            raise AssertionError(f'empty or invalid reply: {reply!r}')
        print(f'OK   {command} -> {text[:120]!r}')
    except Exception as exc:
        failed.append((command,repr(exc)))
        print(f'FAIL {command}: {exc!r}')

app.destroy()

if failed:
    print('\nFAILED COMMANDS')
    for command,error in failed:
        print(f'{command}: {error}')
    raise SystemExit(1)

print('\nULTRON safe command smoke tests passed.')
