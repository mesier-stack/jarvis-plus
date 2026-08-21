from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

from jarvis_core import AssistantReply, JarvisBrain

SEARCH_ROOTS = [Path.home() / name for name in ("Desktop", "Documents", "Downloads", "Pictures")]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip(" .!?¿¡"))


def _iter_files(limit: int = 4000):
    count = 0
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                yield path
                count += 1
                if count >= limit:
                    return


def _find_files(query: str, max_results: int = 8):
    terms = [t for t in re.split(r"\s+", query.lower()) if t]
    matches = []
    for path in _iter_files():
        name = path.name.lower()
        score = sum(1 for t in terms if t in name)
        if score:
            try:
                mtime = path.stat().st_mtime
            except OSError:
                mtime = 0
            matches.append((score, mtime, path))
    matches.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [m[2] for m in matches[:max_results]]


def _recent_files(hours: int = 24, max_results: int = 8):
    cutoff = datetime.now().timestamp() - hours * 3600
    items = []
    for path in _iter_files():
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime >= cutoff:
            items.append((mtime, path))
    items.sort(reverse=True)
    return [p for _, p in items[:max_results]]


def _format_paths(paths):
    if not paths:
        return "No matching files found."
    lines = []
    for path in paths:
        try:
            stamp = datetime.fromtimestamp(path.stat().st_mtime).strftime("%d %b %H:%M")
        except OSError:
            stamp = "unknown"
        lines.append(f"• {path.name}  [{stamp}]\n  {path}")
    return "\n".join(lines)


def install_file_intelligence_patch() -> None:
    if getattr(JarvisBrain, "_ultron_files_installed", False):
        return
    original = JarvisBrain.handle

    def handle_files(self: JarvisBrain, raw: str) -> AssistantReply:
        low = _norm(raw)

        recent_patterns = {
            "recent files", "latest files", "archivos recientes", "mis archivos recientes",
            "what files did i download today", "qué archivos descargué hoy", "que archivos descargue hoy",
        }
        if low in recent_patterns:
            paths = _recent_files(24)
            intro = "Archivos recientes:" if "archivo" in low or "qué" in low or "que " in low else "Recent files:"
            return AssistantReply(intro + "\n" + _format_paths(paths), "files")

        match = re.match(r"^(?:find file|find files|search files|busca archivo|buscar archivo|encuentra archivo)\s+(.+)$", raw, re.I)
        if match:
            query = match.group(1).strip()
            paths = _find_files(query)
            intro = "Encontré:" if re.search(r"busca|buscar|encuentra", raw, re.I) else "I found:"
            return AssistantReply(intro + "\n" + _format_paths(paths), "files")

        return original(self, raw)

    JarvisBrain.handle = handle_files
    JarvisBrain._ultron_files_installed = True
