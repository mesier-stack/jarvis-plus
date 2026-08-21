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
app.destroy()
print('ULTRON app construction smoke test passed')
