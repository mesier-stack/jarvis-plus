from __future__ import annotations

import importlib
import pathlib

failed=[]
for path in sorted(pathlib.Path('.').glob('ultron*.py')):
    name=path.stem
    try:
        importlib.import_module(name)
        print(f'OK   {name}')
    except Exception as exc:
        failed.append((name,repr(exc)))
        print(f'FAIL {name}: {exc!r}')

if failed:
    print('\nFAILED MODULES')
    for name,error in failed:
        print(f'{name}: {error}')
    raise SystemExit(1)

print('\nAll ULTRON modules imported successfully.')
