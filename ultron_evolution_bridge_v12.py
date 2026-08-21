from __future__ import annotations
import time
from ultron_evolution_v11 import evolution_state
from ultron_evolution_telemetry_v12 import record_generation_sample, maybe_auto_revert

def install_evolution_bridge_v12(app_cls):
    if getattr(app_cls,'_evolution_bridge_v12',False):return
    old_process=app_cls._process;old_handle=app_cls._handle_reply
    def process(self,text):
        self._evo_started=time.perf_counter();return old_process(self,text)
    def handle_reply(self,reply):
        result=old_handle(self,reply)
        try:
            elapsed=(time.perf_counter()-getattr(self,'_evo_started',time.perf_counter()))*1000
            gen=int(evolution_state().get('generation',1));kind=getattr(reply,'kind','answer');success=kind!='error';fitness=record_generation_sample(gen,success,elapsed,error=not success);self._evolution_fitness=fitness
            reverted,msg=maybe_auto_revert()
            if reverted:self._system(msg)
        except Exception:pass
        return result
    def evolution_visual_state(self):
        s=evolution_state();return {'generation':s.get('generation',1),'router_bias':s.get('router_bias',{}),'retry_budget':s.get('retry_budget',2),'vision_threshold':s.get('vision_threshold',.55),'memory_weight':s.get('memory_weight',1.0),'fitness':getattr(self,'_evolution_fitness',0)}
    app_cls._process=process;app_cls._handle_reply=handle_reply;app_cls._evolution_visual_state=evolution_visual_state;app_cls._evolution_bridge_v12=True