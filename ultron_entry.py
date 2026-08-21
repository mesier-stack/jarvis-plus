from ultron_identity import install_identity_patch
from ultron_vision import install_vision_patch
from ultron_health import install_health_patch
from ultron_focus import install_focus_patch
from ultron_awareness import install_awareness_patch
from ultron_bilingual import install_bilingual_patch
from ultron_files import install_file_intelligence_patch
from ultron_planner import install_planner_patch
from ultron_windows import install_window_control_patch

install_identity_patch()
install_vision_patch()
install_health_patch()
install_focus_patch()
install_awareness_patch()
install_bilingual_patch()
install_file_intelligence_patch()
install_planner_patch()
install_window_control_patch()

import ultron_main
from ultron_brain_ui import install_brain_ui
from ultron_overlay import install_overlay
from ultron_watch import install_watch_mode

install_brain_ui(ultron_main.UltronApp)
install_overlay(ultron_main.UltronApp)
install_watch_mode(ultron_main.UltronApp)

if __name__ == "__main__":
    app = ultron_main.UltronApp()
    app.mainloop()
