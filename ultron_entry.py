from ultron_identity import install_identity_patch
from ultron_vision import install_vision_patch
from ultron_health import install_health_patch
from ultron_focus import install_focus_patch

install_identity_patch()
install_vision_patch()
install_health_patch()
install_focus_patch()

import runpy

runpy.run_path("ultron_main.py", run_name="__main__")
