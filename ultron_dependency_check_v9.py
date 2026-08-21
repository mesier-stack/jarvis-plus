from __future__ import annotations
import importlib.util
from ultron_core import AssistantReply,UltronBrain
REQ={'customtkinter':'customtkinter','psutil':'psutil','Pillow':'PIL','sounddevice':'sounddevice','numpy':'numpy','openai':'openai','pystray':'pystray'}
def install_dependency_check_v9():
    if getattr(UltronBrain,'_deps_v9',False): return
    old=UltronBrain.handle
    def handle(self,raw):
        low=raw.lower().strip(' .!?¿¡')
        if low in {'dependency check','check dependencies','revisa dependencias','dependencias'}:
            rows=[];missing=[]
            for label,module in REQ.items():
                ok=importlib.util.find_spec(module) is not None;rows.append(f"{'OK' if ok else 'MISS'} // {label}")
                if not ok: missing.append(label)
            head='DEPENDENCY CORE // HEALTHY' if not missing else f"DEPENDENCY CORE // {len(missing)} MISSING"
            return AssistantReply(head+'\n'+'\n'.join(rows),'status' if not missing else 'error')
        return old(self,raw)
    UltronBrain.handle=handle;UltronBrain._deps_v9=True