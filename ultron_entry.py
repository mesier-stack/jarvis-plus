from ultron_vision import install_vision_patch

install_vision_patch()

import runpy

runpy.run_path("ultron_main.py", run_name="__main__")
