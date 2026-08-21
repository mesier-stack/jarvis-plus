from ultron_identity import install_identity_patch
from ultron_vision import install_vision_patch
from ultron_health import install_health_patch
from ultron_focus import install_focus_patch
from ultron_awareness import install_awareness_patch
from ultron_bilingual import install_bilingual_patch
from ultron_files import install_file_intelligence_patch
from ultron_planner import install_planner_patch
from ultron_windows import install_window_control_patch
from ultron_permissions import install_permission_patch
from ultron_memory_categories import install_memory_category_patch
from ultron_updater import install_update_check_patch
from ultron_action_history import install_action_history_patch

install_identity_patch()
install_vision_patch()
install_health_patch()
install_focus_patch()
install_awareness_patch()
install_bilingual_patch()
install_file_intelligence_patch()
install_planner_patch()
install_window_control_patch()
install_permission_patch()
install_memory_category_patch()
install_update_check_patch()
install_action_history_patch()

import ultron_main
from ultron_brain_ui import install_brain_ui
from ultron_overlay import install_overlay
from ultron_watch import install_watch_mode
from ultron_conversation import install_conversation_mode
from ultron_command_center import install_command_center

install_brain_ui(ultron_main.UltronApp)
install_overlay(ultron_main.UltronApp)
install_watch_mode(ultron_main.UltronApp)
install_conversation_mode(ultron_main.UltronApp)
install_command_center(ultron_main.UltronApp)

if __name__ == "__main__":
    app = ultron_main.UltronApp()
    app.mainloop()
