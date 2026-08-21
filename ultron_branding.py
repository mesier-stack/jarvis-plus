from __future__ import annotations

import os
import shutil
from pathlib import Path


def install_ultron_branding() -> None:
    """Make the inherited engine behave as ULTRON without exposing legacy branding."""
    # New public environment variable names. Legacy aliases are populated only in-process
    # so older engine code remains compatible while users configure ULTRON_* names.
    aliases = {
        "ULTRON_VOICE": "JARVIS_VOICE",
        "ULTRON_CLOUD_VOICE": "JARVIS_CLOUD_VOICE",
    }
    for public, legacy in aliases.items():
        if os.getenv(public) and not os.getenv(legacy):
            os.environ[legacy] = os.environ[public]

    import jarvis_core as core

    core.APP_NAME = "ULTRON"
    appdata = Path(os.getenv("APPDATA") or Path.home())
    data_dir = Path(os.getenv("ULTRON_DATA_DIR") or (appdata / "ULTRON"))
    data_dir.mkdir(parents=True, exist_ok=True)
    core.DATA_DIR = data_dir

    # One-time private-memory migration from an older local install, if present.
    old_db = appdata / "JarvisPlus" / "jarvis.db"
    new_db = data_dir / "ultron.db"
    if old_db.is_file() and not new_db.exists():
        try:
            shutil.copy2(old_db, new_db)
        except OSError:
            pass

    original_memory_init = core.MemoryStore.__init__

    def memory_init(self, path=None):
        return original_memory_init(self, path or (data_dir / "ultron.db"))

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
