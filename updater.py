from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from version import VERSION


DEFAULT_MANIFEST_URL = (
    "https://raw.githubusercontent.com/mesier-stack/jarvis-plus/main/update_manifest.json"
)
MAX_UPDATE_BYTES = 50 * 1024 * 1024
UPDATABLE_FILES = {
    "main.py",
    "jarvis_core.py",
    "updater.py",
    "version.py",
    "requirements.txt",
    "README.md",
    "run_jarvis.bat",
    "build_exe.bat",
    ".env.example",
    "tests/test_core.py",
}


@dataclass(frozen=True)
class UpdateInfo:
    version: str
    download_url: str
    sha256: str
    notes: str = ""


def version_tuple(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(piece) for piece in value.strip().lstrip("v").split("."))
    except ValueError as exc:
        raise ValueError(f"Invalid update version: {value}") from exc


class UpdateClient:
    def __init__(self, manifest_url: str | None = None) -> None:
        self.manifest_url = manifest_url or os.getenv("JARVIS_UPDATE_MANIFEST", DEFAULT_MANIFEST_URL)

    def check(self, timeout: float = 5.0) -> UpdateInfo | None:
        request = urllib.request.Request(
            self.manifest_url,
            headers={"User-Agent": f"JARVIS-Plus/{VERSION}"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read(256 * 1024).decode("utf-8"))
        info = UpdateInfo(
            version=str(payload["version"]),
            download_url=str(payload["download_url"]),
            sha256=str(payload["sha256"]).lower(),
            notes=str(payload.get("notes", "")),
        )
        if not info.download_url.startswith("https://"):
            raise ValueError("Update download must use HTTPS")
        if len(info.sha256) != 64 or any(c not in "0123456789abcdef" for c in info.sha256):
            raise ValueError("Update checksum is invalid")
        return info if version_tuple(info.version) > version_tuple(VERSION) else None

    def stage_and_launch(self, info: UpdateInfo, install_dir: Path | None = None) -> None:
        install_dir = (install_dir or Path(__file__).resolve().parent).resolve()
        request = urllib.request.Request(
            info.download_url,
            headers={"User-Agent": f"JARVIS-Plus/{VERSION}"},
        )
        update_dir = Path(tempfile.mkdtemp(prefix="jarvis-plus-update-"))
        archive = update_dir / "update.zip"
        digest = hashlib.sha256()
        total = 0
        try:
            with urllib.request.urlopen(request, timeout=30) as response, archive.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > MAX_UPDATE_BYTES:
                        raise ValueError("Update package is unexpectedly large")
                    digest.update(chunk)
                    output.write(chunk)
            if digest.hexdigest() != info.sha256:
                raise ValueError("Update verification failed; nothing was changed")

            flags = 0
            if os.name == "nt":
                flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            subprocess.Popen(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--apply",
                    str(archive),
                    str(install_dir),
                    str(os.getpid()),
                    info.version,
                ],
                cwd=str(install_dir),
                creationflags=flags,
                close_fds=True,
            )
        except Exception:
            shutil.rmtree(update_dir, ignore_errors=True)
            raise


def _safe_archive_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    selected: list[zipfile.ZipInfo] = []
    for member in archive.infolist():
        path = PurePosixPath(member.filename)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Unsafe path in update package")
        normalized = path.as_posix().rstrip("/")
        if not normalized or member.is_dir():
            continue
        if normalized not in UPDATABLE_FILES:
            raise ValueError(f"Unexpected file in update package: {normalized}")
        selected.append(member)
    required = {"main.py", "jarvis_core.py", "updater.py", "version.py", "run_jarvis.bat"}
    if not required.issubset({PurePosixPath(m.filename).as_posix() for m in selected}):
        raise ValueError("Update package is incomplete")
    return selected


def apply_staged_update(archive_path: Path, install_dir: Path, parent_pid: int) -> None:
    for _ in range(120):
        try:
            os.kill(parent_pid, 0)
        except OSError:
            break
        time.sleep(0.25)

    staging = archive_path.parent / "extracted"
    backup = archive_path.parent / "backup"
    staging.mkdir()
    backup.mkdir()
    replaced: list[str] = []
    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = _safe_archive_members(archive)
            for member in members:
                archive.extract(member, staging)

        for relative in sorted(UPDATABLE_FILES):
            source = staging / relative
            if not source.is_file():
                continue
            target = install_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                saved = backup / relative
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, saved)
            shutil.copy2(source, target)
            replaced.append(relative)
    except Exception:
        for relative in reversed(replaced):
            saved = backup / relative
            target = install_dir / relative
            if saved.exists():
                shutil.copy2(saved, target)
        raise

    if os.name == "nt":
        subprocess.Popen(
            ["cmd", "/c", "start", "", str(install_dir / "run_jarvis.bat")],
            cwd=str(install_dir),
            creationflags=subprocess.DETACHED_PROCESS,
        )


def _main() -> int:
    if len(sys.argv) == 6 and sys.argv[1] == "--apply":
        archive = Path(sys.argv[2]).resolve()
        install = Path(sys.argv[3]).resolve()
        parent_pid = int(sys.argv[4])
        apply_staged_update(archive, install, parent_pid)
        shutil.rmtree(archive.parent, ignore_errors=True)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(_main())

