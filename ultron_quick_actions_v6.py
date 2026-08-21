from __future__ import annotations
import json
from ultron_core import AssistantReply, UltronBrain

DEFAULTS=["test nvidia","look at my screen","ultron status","what do you remember","focus mode"]

def _load(memory):
    try:
        data=json.loads(memory.get_setting("ultron_favorites","[]")); return data if isinstance(data,list) else DEFAULTS[:]
    except Exception: return DEFAULTS[:]

def _save(memory,items): memory.set_setting("ultron_favorites",json.dumps(items[:12]))

def install_quick_actions_v6():
    if getattr(UltronBrain,"_quick_actions_v6",False): return
    old=UltronBrain.handle
    def handle(self,raw):
        low=raw.strip(); norm=low.lower()
        if norm.startswith("favorite ") or norm.startswith("favourite "):
            cmd=low.split(" ",1)[1].strip(); items=_load(self.memory)
            if cmd and cmd not in items: items.append(cmd); _save(self.memory,items)
            return AssistantReply("FAVORITES // "+" | ".join(items),"status")
        if norm.startswith("unfavorite "):
            cmd=low.split(" ",1)[1].strip(); items=[x for x in _load(self.memory) if x.lower()!=cmd.lower()]; _save(self.memory,items)
            return AssistantReply("FAVORITES // "+(" | ".join(items) if items else "EMPTY"),"status")
        if norm in {"favorites","favourites","quick actions","acciones rápidas","acciones rapidas"}:
            return AssistantReply("QUICK ACTIONS\n"+"\n".join(f"• {x}" for x in _load(self.memory)),"status")
        return old(self,raw)
    UltronBrain.handle=handle; UltronBrain._quick_actions_v6=True