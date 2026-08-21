from __future__ import annotations
from ultron_brain_v4 import BrainV4, Node
from ultron_evolution_v11 import evolution_state

def install_brain_evolution_v12(app_cls):
    if getattr(BrainV4,'_evolution_visual_v12',False): return
    old_nodes=BrainV4._nodes; old_links=BrainV4._links; old_status=BrainV4._status; old_poll=BrainV4._poll
    def nodes(self):
        out=old_nodes(self)
        out.append(Node('evolution','EVOLUTION',1.85,.15,'ai','Self-rewiring generations, fitness and guarded optimization.'))
        return out
    def links(self): return old_links(self)+[('core','evolution'),('evolution','router'),('evolution','recovery')]
    def status(self,key):
        if key=='evolution':
            s=evolution_state(); fit=getattr(self.app,'_evolution_fitness',0); return True,f"GEN {s.get('generation',1)} // FITNESS {fit:.1f}"
        return old_status(self,key)
    def poll(self):
        try:
            s=evolution_state(); gen=s.get('generation',1); fit=getattr(self.app,'_evolution_fitness',0)
            marker=f"GEN {gen} // FITNESS {fit:.1f}"
            if getattr(self,'_last_evo_marker',None)!=marker:
                self.timeline.appendleft(f"EVOLUTION  {marker}"); self._last_evo_marker=marker
        except Exception: pass
        return old_poll(self)
    BrainV4._nodes=nodes;BrainV4._links=links;BrainV4._status=status;BrainV4._poll=poll;BrainV4._evolution_visual_v12=True