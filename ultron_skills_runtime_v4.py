from __future__ import annotations

import json
from pathlib import Path

from ultron_core import AssistantReply, UltronBrain

SKILLS_DIR=Path(__file__).resolve().parent/"skills"

def _manifests():
    SKILLS_DIR.mkdir(exist_ok=True)
    out=[]
    for manifest in SKILLS_DIR.glob("*/manifest.json"):
        try:
            data=json.loads(manifest.read_text(encoding="utf-8")); data["path"]=str(manifest.parent); out.append(data)
        except Exception: continue
    return out

def install_skills_runtime_v4():
    if getattr(UltronBrain,"_skills_runtime_v4",False): return
    old=UltronBrain.handle
    def handle(self,raw):
        low=raw.lower().strip(" .!?¿¡")
        if low in {"skills","list skills","show skills","habilidades"}:
            skills=_manifests()
            if not skills: return AssistantReply("Skills directory is ready. No external skills are installed yet.","status")
            lines=["SKILL REGISTRY"]
            for s in skills: lines.append(f"- {s.get('name','Unnamed')} // {s.get('version','0')} // {s.get('status','disabled')}")
            return AssistantReply("\n".join(lines),"status")
        return old(self,raw)
    UltronBrain.handle=handle; UltronBrain._skills_runtime_v4=True
