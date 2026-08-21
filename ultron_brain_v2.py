from __future__ import annotations

from ultron_activity import get_activity


def install_brain_v2() -> None:
    from ultron_brain_ui import BrainWindow
    if getattr(BrainWindow, "_ultron_v2_installed", False):
        return

    original_status = BrainWindow._status_map
    original_refresh = BrainWindow._refresh_status

    def status_map(self):
        status = original_status(self)
        status["planner"] = (True, "ONLINE")
        status["files"] = (True, "ONLINE")
        status["permissions"] = (True, "CONFIGURABLE")
        status["screen_context"] = (True, "CHANGE AWARE")
        return status

    def refresh_status(self):
        state = get_activity()
        lane = state.get("lane", "standby").upper()
        detail = state.get("detail", "")
        try:
            self.activity_label.configure(text=f"COGNITION // {lane}")
            active = lane != "STANDBY"
            self.activity_bar.set(0.82 if active else 0.18)
            self.activity_pct.configure(text="82%" if active else "18%")
            if detail:
                self.stats.configure(text=f"ACTIVE LANE // {lane}")
        except Exception:
            pass
        original_refresh(self)

    BrainWindow._status_map = status_map
    BrainWindow._refresh_status = refresh_status
    BrainWindow._ultron_v2_installed = True
