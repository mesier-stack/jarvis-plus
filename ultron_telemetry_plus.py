from __future__ import annotations

import shutil


def telemetry_snapshot() -> dict[str, str]:
    data = {"cpu": "--", "ram": "--", "disk": "--", "network": "--", "gpu": "N/A"}
    try:
        import psutil
        data["cpu"] = f"{psutil.cpu_percent(interval=None):.0f}%"
        data["ram"] = f"{psutil.virtual_memory().percent:.0f}%"
        data["disk"] = f"{psutil.disk_usage('/').percent:.0f}%"
        io = psutil.net_io_counters()
        data["network"] = f"↑ {io.bytes_sent/1048576:.0f} MB  ↓ {io.bytes_recv/1048576:.0f} MB"
    except Exception:
        pass
    try:
        import subprocess
        if shutil.which("nvidia-smi"):
            out = subprocess.check_output([
                "nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
                "--format=csv,noheader,nounits"
            ], text=True, timeout=2).strip().splitlines()[0]
            util, used, total, temp = [x.strip() for x in out.split(",")]
            data["gpu"] = f"{util}% · {used}/{total} MB · {temp}°C"
    except Exception:
        pass
    return data
