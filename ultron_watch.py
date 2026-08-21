from __future__ import annotations

import threading
import time
from pathlib import Path


def install_watch_mode(app_class) -> None:
    original_init = app_class.__init__
    original_close = app_class._close

    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._watch_stop = threading.Event()
        self._watch_baseline = {}
        self._watch_thread = None
        self.bind("<Control-Shift-w>", lambda _e: self._toggle_watch_mode())
        self._system("CTRL+SHIFT+W = WATCH DOWNLOADS")

    def _toggle_watch_mode(self):
        if self._watch_thread and self._watch_thread.is_alive():
            self._watch_stop.set()
            self._system("WATCH MODE // STOPPING")
            return
        folder = Path.home() / "Downloads"
        folder.mkdir(parents=True, exist_ok=True)
        self._watch_stop.clear()
        self._watch_baseline = {
            str(p): p.stat().st_mtime for p in folder.iterdir() if p.is_file()
        }
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watch_thread.start()
        self._system("WATCH MODE // DOWNLOADS ACTIVE")

    def _watch_loop(self):
        folder = Path.home() / "Downloads"
        while not self._watch_stop.wait(2.0):
            try:
                current = {str(p): p.stat().st_mtime for p in folder.iterdir() if p.is_file()}
            except Exception:
                continue
            new_files = [Path(p) for p in current if p not in self._watch_baseline]
            completed = [p for p in new_files if not p.name.lower().endswith((".crdownload", ".part", ".tmp"))]
            if completed:
                names = ", ".join(p.name for p in completed[:3])
                self.inbox.put(("watch_notice", f"DOWNLOAD DETECTED // {names}"))
            self._watch_baseline = current
        self.inbox.put(("watch_notice", "WATCH MODE // OFFLINE"))

    app_class._toggle_watch_mode = _toggle_watch_mode
    app_class._watch_loop = _watch_loop

    old_drain = app_class._drain_inbox
    def drain_with_watch(self):
        try:
            import queue
            pending = []
            while True:
                item = self.inbox.get_nowait()
                if item[0] == "watch_notice":
                    self._system(str(item[1]))
                else:
                    pending.append(item)
        except queue.Empty:
            pass
        for item in pending:
            self.inbox.put(item)
        old_drain(self)
    app_class._drain_inbox = drain_with_watch

    def close_with_watch(self):
        try:
            self._watch_stop.set()
        except Exception:
            pass
        original_close(self)
    app_class._close = close_with_watch

    app_class.__init__ = new_init
