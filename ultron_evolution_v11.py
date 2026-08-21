from __future__ import annotations
import json, os, time
from pathlib import Path
from ultron_core import AssistantReply, UltronBrain

DATA=Path(os.getenv('APPDATA',Path.home()))/'ULTRON'/'evolution.json'
DEFAULT={
  'generation':1,
  'router_bias':{'learned':1.0,'builtin':1.0,'ai':1.0,'vision':1.0},
  'retry_budget':2,
  'vision_threshold':0.55,
  'memory_weight':1.0,
  'candidates':[],
  'history':[]
}

def _load():
    try:
        d=json.loads(DATA.read_text(encoding='utf-8'))
        base=DEFAULT.copy(); base.update(d); return base
    except Exception: return json.loads(json.dumps(DEFAULT))

def _save(d):
    DATA.parent.mkdir(parents=True,exist_ok=True); DATA.write_text(json.dumps(d,indent=2),encoding='utf-8')

def _snapshot(d,reason):
    d['history']=(d.get('history') or [])[-24:]+[{'ts':time.time(),'reason':reason,'state':{k:d[k] for k in ('generation','router_bias','retry_budget','vision_threshold','memory_weight')}}]

def propose_from_learning(brain):
    d=_load(); learned=brain.memory.get_setting('ultron_last_learning_summary','')
    candidate={'created':time.time(),'status':'proposed','changes':{},'reason':'learning telemetry'}
    try:
        stats=getattr(brain,'learning_store',None)
        if stats and hasattr(stats,'best_routes'):
            routes=stats.best_routes()
            for name,score in routes.items():
                if name in d['router_bias']:
                    candidate['changes'].setdefault('router_bias',{})[name]=max(.5,min(1.8,float(score)))
    except Exception: pass
    if not candidate['changes']:
        rb=dict(d['router_bias']); rb['learned']=min(1.5,rb.get('learned',1.0)+.05); candidate['changes']['router_bias']=rb
    d['candidates']=(d.get('candidates') or [])[-9:]+[candidate]; _save(d); return candidate

def evaluate_candidate(candidate):
    # Configuration-only candidates are constrained to bounded numeric ranges.
    ch=candidate.get('changes',{})
    rb=ch.get('router_bias',{})
    if any(not (.25 <= float(v) <= 2.0) for v in rb.values()): return False,'router bias out of bounds'
    if 'retry_budget' in ch and not (0 <= int(ch['retry_budget']) <= 4): return False,'retry budget out of bounds'
    if 'vision_threshold' in ch and not (.2 <= float(ch['vision_threshold']) <= .95): return False,'vision threshold out of bounds'
    if 'memory_weight' in ch and not (.25 <= float(ch['memory_weight']) <= 2.0): return False,'memory weight out of bounds'
    return True,'candidate passed invariant checks'

def promote_latest():
    d=_load(); candidates=d.get('candidates') or []
    if not candidates: return False,'No evolution candidate exists.'
    c=candidates[-1]; ok,reason=evaluate_candidate(c)
    if not ok: c['status']='rejected'; c['result']=reason; _save(d); return False,reason
    _snapshot(d,'pre-promotion')
    for k,v in c.get('changes',{}).items():
        if k=='router_bias': d[k].update(v)
        elif k in {'retry_budget','vision_threshold','memory_weight'}: d[k]=v
    d['generation']=int(d.get('generation',1))+1; c['status']='promoted'; c['result']=reason; _save(d)
    return True,f"Generation {d['generation']} promoted."

def rollback_generation():
    d=_load(); hist=d.get('history') or []
    if not hist: return False,'No evolution snapshot available.'
    snap=hist.pop()['state']
    for k,v in snap.items(): d[k]=v
    d['history']=hist; _save(d); return True,f"Rolled back to generation {d.get('generation',1)}."

def evolution_state(): return _load()

def install_evolution_v11():
    if getattr(UltronBrain,'_evolution_v11',False): return
    old=UltronBrain.handle
    def handle(self,raw):
        low=raw.lower().strip(' .!?¿¡')
        if low in {'evolution status','evolution','self rewiring status','rewiring status'}:
            d=_load(); rb=' / '.join(f'{k}:{v:.2f}' for k,v in d['router_bias'].items())
            return AssistantReply(f"EVOLUTION ENGINE // ONLINE\nGENERATION // {d['generation']}\nROUTER // {rb}\nRETRY BUDGET // {d['retry_budget']}\nVISION THRESHOLD // {d['vision_threshold']:.2f}\nMEMORY WEIGHT // {d['memory_weight']:.2f}\nCANDIDATES // {len(d.get('candidates') or [])}",'status')
        if low in {'propose evolution','evolve','rewire yourself','self optimize'}:
            c=propose_from_learning(self); return AssistantReply(f"EVOLUTION CANDIDATE // PROPOSED\nCHANGES // {c['changes']}\nSay 'promote evolution' to apply after invariant checks.",'status')
        if low in {'promote evolution','apply evolution','promote candidate'}:
            ok,msg=promote_latest(); return AssistantReply(('EVOLUTION // PROMOTED\n' if ok else 'EVOLUTION // REJECTED\n')+msg,'status' if ok else 'error')
        if low in {'rollback evolution','rollback generation'}:
            ok,msg=rollback_generation(); return AssistantReply(msg,'status' if ok else 'error')
        return old(self,raw)
    UltronBrain.handle=handle; UltronBrain._evolution_v11=True