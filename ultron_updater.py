from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from ultron_core import AssistantReply, UltronBrain

REPO_API = "https://api.github.com/repos/mesier-stack/jarvis-plus/commits/main"
REPO_ZIP = "https://github.com/mesier-stack/jarvis-plus/archive/refs/heads/main.zip"
MAX_UPDATE_BYTES = 20 * 1024 * 1024


def _data_dir() -> Path:
    root=Path(os.getenv("ULTRON_DATA_DIR") or os.getenv("APPDATA") or Path.home())/"ULTRON"
    root.mkdir(parents=True,exist_ok=True); return root

def _backup_dir() -> Path:
    return _data_dir()/"backups"/"latest"

def _latest_sha() -> str:
    req=urllib.request.Request(REPO_API,headers={"User-Agent":"ULTRON-Updater"})
    with urllib.request.urlopen(req,timeout=8) as response:
        data=json.loads(response.read().decode("utf-8"))
    return str(data.get("sha", ""))

def _launch_update(install_dir: Path) -> None:
    temp_dir=Path(tempfile.mkdtemp(prefix="ultron-update-")); archive_path=temp_dir/"main.zip"; script_path=temp_dir/"apply_update.py"
    request=urllib.request.Request(REPO_ZIP,headers={"User-Agent":"ULTRON-Updater"}); total=0
    with urllib.request.urlopen(request,timeout=30) as response, archive_path.open("wb") as output:
        while True:
            chunk=response.read(1024*1024)
            if not chunk: break
            total+=len(chunk)
            if total>MAX_UPDATE_BYTES: raise RuntimeError("Update package is unexpectedly large")
            output.write(chunk)
    backup=_backup_dir()
    helper=r'''from __future__ import annotations
import os, shutil, subprocess, sys, time, zipfile
from pathlib import Path, PurePosixPath
archive=Path(sys.argv[1]).resolve(); install=Path(sys.argv[2]).resolve(); parent_pid=int(sys.argv[3]); backup=Path(sys.argv[4]).resolve()
for _ in range(160):
    try: os.kill(parent_pid,0)
    except OSError: break
    time.sleep(.25)
if backup.exists(): shutil.rmtree(backup,ignore_errors=True)
backup.mkdir(parents=True,exist_ok=True)
for source in install.rglob("*"):
    if not source.is_file(): continue
    rel=source.relative_to(install)
    if rel.parts and rel.parts[0] in {".git",".venv","__pycache__"}: continue
    target=backup/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
staging=archive.parent/"staging"; staging.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
    for member in z.infolist():
        path=PurePosixPath(member.filename)
        if path.is_absolute() or ".." in path.parts: raise RuntimeError("Unsafe update path")
        z.extract(member,staging)
roots=[p for p in staging.iterdir() if p.is_dir()]
if len(roots)!=1: raise RuntimeError("Unexpected update layout")
source_root=roots[0]
for source in source_root.rglob("*"):
    if not source.is_file(): continue
    rel=source.relative_to(source_root)
    if rel.parts and rel.parts[0] in {".git","__pycache__"}: continue
    target=install/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
requirements=install/"requirements.txt"
if requirements.exists(): subprocess.run([sys.executable,"-m","pip","install","-r",str(requirements)],cwd=str(install),check=False)
subprocess.Popen([sys.executable,str(install/"ultron_entry.py")],cwd=str(install)); shutil.rmtree(archive.parent,ignore_errors=True)
'''
    script_path.write_text(helper,encoding="utf-8")
    flags=0
    if os.name=="nt": flags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS
    subprocess.Popen([sys.executable,str(script_path),str(archive_path),str(install_dir),str(os.getpid()),str(backup)],cwd=str(install_dir),creationflags=flags,close_fds=True)

def _rollback(install_dir: Path) -> str:
    backup=_backup_dir()
    if not backup.exists() or not any(backup.rglob("*")): return "No rollback backup is available yet."
    restored=0
    for source in backup.rglob("*"):
        if not source.is_file(): continue
        rel=source.relative_to(backup); target=install_dir/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target); restored+=1
    return f"Rollback restored {restored} application files. Restart ULTRON to load the previous build."

def install_update_check_patch() -> None:
    if getattr(UltronBrain,"_ultron_updater_installed",False): return
    original=UltronBrain.handle
    def wrapped(self: UltronBrain,raw:str)->AssistantReply:
        low=raw.lower().strip(" .!?¿¡")
        if low in {"check for updates","check updates","buscar actualizaciones","revisa actualizaciones"}:
            try:
                sha=_latest_sha()
                if not sha: raise RuntimeError("No commit SHA returned")
                previous=self.memory.get_setting("ultron_last_seen_commit",""); self.memory.set_setting("ultron_last_seen_commit",sha)
                if previous and previous!=sha: return AssistantReply("A newer ULTRON revision is available. Say 'update ultron' to install it.","status")
                return AssistantReply("Repository check complete. No unseen revision detected.","status")
            except Exception as exc: return AssistantReply(f"Update check failed: {exc}","error")
        if low in {"update ultron","actualiza ultron","actualizar ultron","install update"}:
            try:
                _launch_update(Path(__file__).resolve().parent)
                return AssistantReply("Update downloaded. Close ULTRON now. A backup of the current build will be created before installation, then ULTRON will reopen automatically.","status")
            except Exception as exc: return AssistantReply(f"Update preparation failed: {exc}","error")
        if low in {"rollback ultron","rollback update","revert update","volver version anterior"}:
            try: return AssistantReply(_rollback(Path(__file__).resolve().parent),"status")
            except Exception as exc: return AssistantReply(f"Rollback failed: {exc}","error")
        return original(self,raw)
    UltronBrain.handle=wrapped; UltronBrain._ultron_updater_installed=True