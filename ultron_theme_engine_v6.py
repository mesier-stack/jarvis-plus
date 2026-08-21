from __future__ import annotations
from ultron_core import AssistantReply, UltronBrain

THEMES={
"ultron red":{"accent":"#FF3045","glow":"#8F1C2B","panel":"#08080B"},
"crimson":{"accent":"#FF1744","glow":"#A1112C","panel":"#09070A"},
"stealth":{"accent":"#D9D9DE","glow":"#4A4A52","panel":"#070709"},
}

def install_theme_engine_v6():
    if getattr(UltronBrain,"_theme_v6",False): return
    old=UltronBrain.handle
    def handle(self,raw):
        low=raw.lower().strip(" .!?¿¡")
        if low.startswith("theme ") or low.startswith("tema "):
            name=low.split(" ",1)[1].strip()
            if name not in THEMES: return AssistantReply("THEMES // "+" | ".join(THEMES),"status")
            self.memory.set_setting("ultron_theme",name)
            for k,v in THEMES[name].items(): self.memory.set_setting(f"ultron_theme_{k}",v)
            return AssistantReply(f"THEME // {name.upper()} // ACTIVE","status")
        if low in {"themes","temas","current theme","tema actual"}:
            return AssistantReply(f"ACTIVE THEME // {self.memory.get_setting('ultron_theme','ultron red').upper()}\nAVAILABLE // "+" | ".join(THEMES),"status")
        return old(self,raw)
    UltronBrain.handle=handle; UltronBrain._theme_v6=True