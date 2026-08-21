from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

from ultron_core import AssistantReply, UltronBrain

REPO_API = "https://api.github.com/repos/mesier-stack/jarvis-plus/commits/main"
REPO_ZIP = "https://github.com/mesier-stack/jarvis-plus/archive/refs/heads/main.zip"
MAX_UPDATE_BYTES = 20 * 1024 * 1024


def _latest_sha() -> str:
    req = urllib.request.Request(REPO_API, headers={"User-Agent": "ULTRON-Updater"})
    with urllib.request.urlopen(req, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data.get("sha", ""))


def _launch_update(install_dir: Path) -> None:
    """Download main and launch a detached updater after ULTRON exits."""
    temp_dir = Path(tempfile.mkdtemp(prefix="ultron-update-"))
    archive_path = temp_dir / "main.zip"
    script_path = temp_dir / "apply_update.py"

    request = urllib.request.Request(REPO_ZIP, headers={"User-Agent": "ULTRON-Updater"})
    total = 0
    with urllib.request.urlopen(request, timeout=30) as response, archive_path.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_UPDATE_BYTES:
                raise RuntimeError("Update package is unexpectedly large")
            output.write(chunk)

    # The helper waits for this ULTRON process to exit, safely overlays repo files,
    # refreshes dependencies, then starts ULTRON again. User environment/API keys
    # live outside the project directory and are never touched.
    helper = r'''from __future__ import annotations
import os, shutil, subprocess, sys, time, zipfile
from pathlib import Path, PurePosixPath

archive = Path(sys.argv[1]).resolve()
install = Path(sys.argv[2]).resolve()
parent_pid = int(sys.argv[3])

for _ in range(160):
    try:
        os.kill(parent_pid, 0)
    except OSError:
        break
    time.sleep(0.25)

staging = archive.parent / "staging"
staging.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
    for member in z.infolist():
        path = PurePosixPath(member.filename)
        if path.is_absolute() or ".." in path.parts:
            raise RuntimeError("Unsafe update path")
        z.extract(member, staging)

roots = [p for p in staging.iterdir() if p.is_dir()]
if len(roots) != 1:
    raise RuntimeError("Unexpected update layout")
source_root = roots[0]

for source in source_root.rglob("*"):
    if not source.is_file():
        continue
    relative = source.relative_to(source_root)
    if relative.parts and relative.parts[0] in {".git", "__pycache__"}:
        continue
    target = install / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

requirements = install / "requirements.txt"
if requirements.exists():
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements)], cwd=str(install), check=False)

entry = install / "ultron_entry.py"
subprocess.Popen([sys.executable, str(entry)], cwd=str(install))
shutil.rmtree(archive.parent, ignore_errors=True)
'''
    script_path.write_text(helper, encoding="utf-8")

    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    subprocess.Popen(
        [sys.executable, str(script_path), str(archive_path), str(install_dir), str(os.getpid())],
        cwd=str(install_dir),
        creationflags=flags,
        close_fds=True,
    )


def install_update_check_patch() -> None:
    if getattr(UltronBrain, "_ultron_updater_installed", False):
        return
    original = UltronBrain.handle

    def wrapped(self: UltronBrain, raw: str) -> AssistantReply:
        low = raw.lower().strip(" .!?¿¡")
        if low in {"check for updates", "check updates", "buscar actualizaciones", "revisa actualizaciones"}:
            try:
                sha = _latest_sha()
                if not sha:
                    raise RuntimeError("No commit SHA returned")
                previous = self.memory.get_setting("ultron_last_seen_commit", "")
                self.memory.set_setting("ultron_last_seen_commit", sha)
                if previous and previous != sha:
                    return AssistantReply(
                        "A newer ULTRON revision is available. Say 'update ultron' to install it.",
                        "status",
                    )
                return AssistantReply("Repository check complete. No unseen revision detected.", "status")
            except Exception as exc:
                return AssistantReply(f"Update check failed: {exc}", "error")

        if low in {"update ultron", "actualiza ultron", "actualizar ultron", "install update"}:
            try:
                _launch_update(Path(__file__).resolve().parent)
                return AssistantReply(
                    "Update downloaded. Close ULTRON now; the updater will replace the program files, refresh dependencies, and reopen me automatically. Your API keys are not touched.",
                    "status",
                )
            except Exception as exc:
                return AssistantReply(f"Update preparation failed: {exc}", "error")

        return original(self, raw)

    UltronBrain.handle = wrapped
    UltronBrain._ultron_updater_installed = True