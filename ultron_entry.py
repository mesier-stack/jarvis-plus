from ultron_identity import install_identity_patch
from ultron_vision import install_vision_patch
from ultron_health import install_health_patch
from ultron_focus import install_focus_patch
from ultron_awareness import install_awareness_patch
from ultron_bilingual import install_bilingual_patch

install_identity_patch()
install_vision_patch()
install_health_patch()
install_focus_patch()
install_awareness_patch()
install_bilingual_patch()

import ultron_main
from ultron_brain_ui import install_brain_ui
from ultron_overlay import install_overlay

install_brain_ui(ultron_main.UltronApp)
install_overlay(ultron_main.UltronApp)

if __name__ == "__main__":
    app = ultron_main.UltronApp()
    app.mainloop()
