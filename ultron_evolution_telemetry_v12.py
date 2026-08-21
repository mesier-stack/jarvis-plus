from __future__ import annotations
import json, os, time
from pathlib import Path
from ultron_core import AssistantReply, UltronBrain
from ultron_evolution_v11 import evolution_state, rollback_generation

DATA=Path(os.getenv('APPDATA',Path.home()))/'ULTRON'/'evolution_telemetry.json'

def _load():
    try:return json.loads(DATA.read_text(encoding='utf-8'))
    except Exception:return {'generation_metrics':{},'last_diff':{},'auto_reverts':0}

def _save(d): DATA.parent.mkdir(parents=True,exist_ok=True);DATA.write_text(json.dumps(d,indent=2),encoding='utf-8')

def record_generation_sample(generation:int,success:bool,latency_ms:float,error:bool=False):
    d=_load();g=d['generation_metrics'].setdefault(str(generation),{'samples':0,'success':0,'errors':0,'latency_total':0.0,'fitness':0.0})
    g['samples']+=1;g['success']+=int(bool(success));g['errors']+=int(bool(error));g['latency_total']+=max(0.0,float(latency_ms))
    rate=g['success']/max(1,g['samples']);err=g['errors']/max(1,g['samples']);avg=g['latency_total']/max(1,g['samples'])
    g['fitness']=round(max(0.0,min(100.0,rate*70+(1-err)*20+max(0,10-min(10,avg/300))))),2);_save(d);return g['fitness']

def set_diff(before,after):
    d=_load();diff={}
    for k in ('router_bias','retry_budget','vision_threshold','memory_weight'):
        if before.get(k)!=after.get(k): diff[k]={'before':before.get(k),'after':after.get(k)}
    d['last_diff']={'ts':time.time(),'changes':diff};_save(d)

def maybe_auto_revert():
    state=evolution_state();gen=int(state.get('generation',1));d=_load();cur=d['generation_metrics'].get(str(gen),{});prev=d['generation_metrics'].get(str(gen-1),{})
    if cur.get('samples',0)<8 or prev.get('samples',0)<8:return False,''
    if float(cur.get('fitness',0))+8 < float(prev.get('fitness',0)):
        ok,msg=rollback_generation()
        if ok:d['auto_reverts']=int(d.get('auto_reverts',0))+1;_save(d);return True,'AUTO-REVERT // generation degraded beyond threshold. '+msg
    return False,''

def install_evolution_telemetry_v12():
    if getattr(UltronBrain,'_evo_telemetry_v12',False):return
    old=UltronBrain.handle
    def handle(self,raw):
        low=raw.lower().strip(' .!?¿¡')
        if low in {'evolution fitness','fitness status','generation fitness'}:
            state=evolution_state();d=_load();gen=str(state.get('generation',1));g=d['generation_metrics'].get(gen,{})
            return AssistantReply(f"EVOLUTION FITNESS // GENERATION {gen}\nSAMPLES // {g.get('samples',0)}\nFITNESS // {g.get('fitness',0)}\nAUTO REVERTS // {d.get('auto_reverts',0)}",'status')
        if low in {'evolution diff','rewiring diff','what changed'}:
            d=_load();return AssistantReply('EVOLUTION DIFF // '+json.dumps(d.get('last_diff',{}),indent=2),'status')
        return old(self,raw)
    UltronBrain.handle=handle;UltronBrain._evo_telemetry_v12=True