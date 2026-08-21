from __future__ import annotations


def install_runtime_v2(app_cls) -> None:
    if getattr(app_cls, "_ultron_runtime_v2_installed", False):
        return

    original_dispatch = app_cls._dispatch
    original_animate = app_cls._animate_core

    def dispatch(self, text: str):
        # User input interrupts speech immediately for more natural conversation.
        try:
            if getattr(self.voice, "is_speaking", False):
                self.voice.stop()
        except Exception:
            pass
        return original_dispatch(self, text)

    def animate_core(self):
        perf = self.brain.memory.get_setting("ultron_performance_mode", "off") == "on"
        if perf:
            counter = getattr(self, "_ultron_perf_frame", 0) + 1
            self._ultron_perf_frame = counter
            if counter % 4 != 0:
                self.after(60, self._animate_core)
                return
        return original_animate(self)

    app_cls._dispatch = dispatch
    app_cls._animate_core = animate_core
    app_cls._ultron_runtime_v2_installed = True
