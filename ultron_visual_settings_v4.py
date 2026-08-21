from __future__ import annotations
import random
from ultron_core import AssistantReply, UltronBrain

def _particles(level):
    count={"low":45,"medium":100,"high":180,"ultra":260}.get(level,100)
    return [{"x":random.random(),"y":random.random(),"vx":random.uniform(-.00035,.00035),"vy":random.uniform(-.00025,.00025),"r":random.choice((1,1,1,2)),"p":random.random()*6.28} for _ in range(count)]

def install_visual_settings_v4(app_cls):
    if getattr(app_cls,"_visual_settings_v4",False): return
    old_init=app_cls.__init__; old_handle=UltronBrain.handle
    def init(self,*a,**k):
        old_init(self,*a,**k)
        level=self.brain.memory.get_setting("ultron_particles","high"); self._v3_particles=_particles(level)
        self._animation_intensity=self.brain.memory.get_setting("ultron_animation","intense")
    def handle(self,raw):
        low=raw.lower().strip(" .!?¿¡")
        mapping={"particles low":("ultron_particles","low"),"particles medium":("ultron_particles","medium"),"particles high":("ultron_particles","high"),"particles ultra":("ultron_particles","ultra"),"particulas bajas":("ultron_particles","low"),"particulas altas":("ultron_particles","high"),"animation calm":("ultron_animation","calm"),"animation intense":("ultron_animation","intense"),"animacion suave":("ultron_animation","calm"),"animacion intensa":("ultron_animation","intense")}
        if low in mapping:
            key,val=mapping[low]; self.memory.set_setting(key,val); return AssistantReply(f"Visual setting updated // {key.replace('ultron_','').upper()} = {val.upper()}. Changes apply immediately where supported.","status")
        return old_handle(self,raw)
    old_dispatch=app_cls._dispatch
    def dispatch(self,text):
        result=old_dispatch(self,text)
        low=text.lower().strip(" .!?¿¡")
        if low.startswith("particles") or low.startswith("particulas"):
            level=self.brain.memory.get_setting("ultron_particles","high"); self._v3_particles=_particles(level)
        return result
    app_cls.__init__=init; app_cls._dispatch=dispatch; UltronBrain.handle=handle; app_cls._visual_settings_v4=True
