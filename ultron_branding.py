from __future__ import annotations

import os
import shutil
from pathlib import Path


def install_ultron_branding() -> None:
    import ultron_core as core

    core.APP_NAME = "ULTRON"
    appdata = Path(os.getenv("APPDATA") or Path.home())
    data_dir = Path(os.getenv("ULTRON_DATA_DIR") or (appdata / "ULTRON"))
    data_dir.mkdir(parents=True, exist_ok=True)
    core.DATA_DIR = data_dir

    # One-time import of data from older local installs. No old branding is used afterward.
    candidates = [p for p in appdata.iterdir() if p.is_dir() and (p / "jarvis.db").is_file()]
    new_db = data_dir / "ultron.db"
    if not new_db.exists():
        for folder in candidates:
            try:
                shutil.copy2(folder / "jarvis.db", new_db)
                break
            except OSError:
                pass

    original_memory_init = core.MemoryStore.__init__
    def memory_init(self, path=None):
        return original_memory_init(self, path or new_db)
    core.MemoryStore.__init__ = memory_init

    def ultron_screenshot():
        try:
            from datetime import datetime
            from PIL import ImageGrab
            folder = Path.home() / "Pictures" / "ULTRON"
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / f"screenshot-{datetime.now():%Y%m%d-%H%M%S}.png"
            ImageGrab.grab().save(path)
            return True, f"Screenshot saved to {path}."
        except Exception as exc:
            return False, f"I couldn't take the screenshot: {exc}"
    core.SystemActions.screenshot = staticmethod(ultron_screenshot)
