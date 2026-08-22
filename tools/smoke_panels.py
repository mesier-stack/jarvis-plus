from __future__ import annotations

import pathlib
import sys
import tkinter as tk

ROOT=pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import ultron_entry
import ultron_main

app=ultron_main.UltronApp()
app.withdraw()
app.update_idletasks()
app.update()

panel_methods=[
    'open_brain',
    'open_control_center',
    '_open_home_v5',
    '_open_diag_v5',
    '_open_notifications_v5',
    'open_memory_center',
    'open_vision_center',
    'open_voice_center',
    '_open_session_analytics_v6',
    '_open_perf_dash_v6',
    '_open_learning_v10',
    '_open_evolution_v11',
    '_open_cognition_v13',
    '_open_web_studio_v14',
    '_shortcut_map_v7',
    '_module_manager_v9',
    '_privacy_v8',
]

failed=[]
for name in panel_methods:
    fn=getattr(app,name,None)
    if not callable(fn):
        failed.append((name,'missing method'))
        print(f'FAIL {name}: missing method')
        continue
    try:
        fn()
        app.update_idletasks()
        app.update()
        print(f'OK   {name}')
    except Exception as exc:
        failed.append((name,repr(exc)))
        print(f'FAIL {name}: {exc!r}')
    finally:
        for child in list(app.winfo_children()):
            if isinstance(child,tk.Toplevel):
                try: child.destroy()
                except Exception: pass

app.destroy()

if failed:
    print('\nFAILED PANELS')
    for name,error in failed:
        print(f'{name}: {error}')
    raise SystemExit(1)

print('\nULTRON panel smoke tests passed.')
