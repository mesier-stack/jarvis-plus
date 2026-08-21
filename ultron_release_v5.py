from __future__ import annotations
import json
from pathlib import Path
from ultron_core import AssistantReply, UltronBrain

ROOT=Path(__file__).resolve().parent

def _version():
    try: return json.loads((ROOT/"VERSION.json").read_text(encoding="utf-8"))
    except Exception: return {"version":"unknown","channel":"stable","build":"unknown","highlights":[]}

def install_release_v5():
    if getattr(UltronBrain,"_release_v5",False): return
    old=UltronBrain.handle
    def handle(self,raw):
        low=raw.lower().strip(" .!?¿¡")
        if low in {"version","ultron version","version status","versión","version ultron"}:
            v=_version(); return AssistantReply(f"ULTRON // {v.get('version')}\nBUILD // {v.get('build')}\nCHANNEL // {self.memory.get_setting('ultron_update_channel',v.get('channel','stable')).upper()}","status")
        if low in {"changelog","what changed","qué cambió","que cambio"}:
            try: txt=(ROOT/"CHANGELOG.md").read_text(encoding="utf-8")[:3500]
            except Exception: txt="Changelog unavailable."
            return AssistantReply(txt,"status")
        if low in {"update channel stable","stable channel","canal estable"}:
            self.memory.set_setting("ultron_update_channel","stable"); return AssistantReply("UPDATE CHANNEL // STABLE","status")
        if low in {"update channel beta","beta channel","canal beta"}:
            self.memory.set_setting("ultron_update_channel","beta"); return AssistantReply("UPDATE CHANNEL // BETA","status")
        return old(self,raw)
    UltronBrain.handle=handle; UltronBrain._release_v5=True