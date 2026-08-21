from __future__ import annotations
import os,time
from pathlib import Path
from ultron_core import AssistantReply,UltronBrain

STAMP=Path(os.getenv('APPDATA',Path.home()))/'ULTRON'/'boot_state.txt'

def install_safe_mode_v9():
    if getattr(UltronBrain,'_safe_mode_v9',False): return
    old=UltronBrain.handle
    def handle(self,raw):
        low=raw.lower().strip(' .!?¿¡')
        if low in {'safe mode','enable safe mode','modo seguro','activar modo seguro'}:
            self.memory.set_setting('ultron_safe_mode','on')
            self.memory.set_setting('ultron_particles','low')
            self.memory.set_setting('ultron_animation','calm')
            self.memory.set_setting('ultron_performance','on')
            return AssistantReply('SAFE MODE // ENABLED\nHeavy visuals reduced and optional modules should remain conservative until disabled.','status')
        if low in {'disable safe mode','normal mode','desactivar modo seguro'}:
            self.memory.set_setting('ultron_safe_mode','off')
            return AssistantReply('SAFE MODE // DISABLED','status')
        if low in {'safe mode status','estado modo seguro'}:
            return AssistantReply(f"SAFE MODE // {self.memory.get_setting('ultron_safe_mode','off').upper()}",'status')
        return old(self,raw)
    UltronBrain.handle=handle;UltronBrain._safe_mode_v9=True

def register_boot_attempt(memory):
    STAMP.parent.mkdir(parents=True,exist_ok=True)
    now=int(time.time()); recent=[]
    if STAMP.exists():
        try: recent=[int(x) for x in STAMP.read_text().splitlines() if x.strip()]
        except Exception: recent=[]
    recent=[x for x in recent if now-x<90];recent.append(now);STAMP.write_text('\n'.join(map(str,recent)))
    if len(recent)>=3: memory.set_setting('ultron_safe_mode','on')

def mark_boot_ok():
    try: STAMP.unlink(missing_ok=True)
    except Exception: pass
