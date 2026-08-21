from __future__ import annotations
from ultron_core import AssistantReply, UltronBrain

PROFILES={
"balanced":{"performance":"off","particles":"high","animation":"intense","voice":"auto"},
"gaming":{"performance":"on","particles":"low","animation":"calm","voice":"off"},
"study":{"performance":"off","particles":"medium","animation":"calm","voice":"auto"},
"cinematic":{"performance":"off","particles":"ultra","animation":"intense","voice":"auto"},
}

def install_profiles_v5():
    if getattr(UltronBrain,"_profiles_v5",False): return
    old=UltronBrain.handle
    def handle(self,raw):
        low=raw.lower().strip(" .!?¿¡")
        aliases={"profile balanced":"balanced","balanced mode":"balanced","profile gaming":"gaming","gaming mode":"gaming","profile study":"study","study mode":"study","profile cinematic":"cinematic","cinematic mode":"cinematic"}
        if low in aliases:
            name=aliases[low]; cfg=PROFILES[name]
            for k,v in cfg.items(): self.memory.set_setting(f"ultron_{k}",v)
            self.memory.set_setting("ultron_profile",name)
            return AssistantReply(f"PROFILE // {name.upper()}\nPerformance: {cfg['performance']}\nParticles: {cfg['particles']}\nAnimation: {cfg['animation']}\nVoice: {cfg['voice']}","status")
        if low in {"current profile","profile status","perfil actual"}:
            return AssistantReply(f"ACTIVE PROFILE // {self.memory.get_setting('ultron_profile','balanced').upper()}","status")
        return old(self,raw)
    UltronBrain.handle=handle; UltronBrain._profiles_v5=True