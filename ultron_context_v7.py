from __future__ import annotations
import os,time
from ultron_core import AssistantReply,UltronBrain

def install_context_v7():
    if getattr(UltronBrain,'_context_v7',False): return
    old=UltronBrain.handle
    def handle(self,raw):
        low=raw.lower().strip(' .!?¿¡')
        if low in {'context status','contexto','what is my context','estado contexto'}:
            hour=time.localtime().tm_hour; period='MORNING' if hour<12 else ('AFTERNOON' if hour<19 else 'NIGHT')
            profile=self.memory.get_setting('ultron_profile','balanced').upper(); lang=self.memory.get_setting('voice_language','auto').upper()
            return AssistantReply(f'CONTEXT ENGINE // ONLINE\nDAYPART // {period}\nPROFILE // {profile}\nLANGUAGE // {lang}\nAI // {getattr(self.ai,"provider","local").upper()}\nVISION // ON DEMAND', 'status')
        return old(self,raw)
    UltronBrain.handle=handle; UltronBrain._context_v7=True