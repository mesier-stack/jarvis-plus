from __future__ import annotations
import customtkinter as ctk
from ultron_evolution_v11 import evolution_state, propose_from_learning, promote_latest, rollback_generation
VOID='#020203';PANEL='#08080B';LINE='#381017';RED='#FF3045';RED_DARK='#410811';WHITE='#F7F7FA';MUTED='#7D7D88';GREEN='#59F6A3';AMBER='#FFBE63'
def install_evolution_ui_v11(app_cls):
    if getattr(app_cls,'_evolution_ui_v11',False): return
    old=app_cls.__init__
    def init(self,*a,**k): old(self,*a,**k); self.bind('<Control-Shift-E>',lambda _e:self._open_evolution_v11())
    def open_evo(self):
        w=ctk.CTkToplevel(self); w.title('ULTRON // Evolution Engine'); w.geometry('820x620'); w.configure(fg_color=VOID); w.transient(self)
        ctk.CTkLabel(w,text='EVOLUTION ENGINE',font=ctk.CTkFont('Segoe UI',28,'bold'),text_color=WHITE).pack(anchor='w',padx=22,pady=(20,2)); ctk.CTkLabel(w,text='CONTROLLED SELF-REWIRING / CONFIG EVOLUTION',font=ctk.CTkFont('Consolas',9,'bold'),text_color=RED).pack(anchor='w',padx=22)
        state=ctk.CTkTextbox(w,height=310,fg_color=PANEL,border_width=1,border_color=LINE,text_color=WHITE,font=ctk.CTkFont('Consolas',10)); state.pack(fill='x',padx=22,pady=18)
        def refresh(msg=''):
            d=evolution_state(); state.configure(state='normal'); state.delete('1.0','end'); state.insert('end',f"GENERATION // {d['generation']}\nRETRY BUDGET // {d['retry_budget']}\nVISION THRESHOLD // {d['vision_threshold']}\nMEMORY WEIGHT // {d['memory_weight']}\n\nROUTER BIAS\n");
            for k,v in d['router_bias'].items(): state.insert('end',f"  {k.upper():<10} {v:.2f}\n")
            state.insert('end',f"\nCANDIDATES // {len(d.get('candidates') or [])}\nSNAPSHOTS // {len(d.get('history') or [])}\n")
            if msg: state.insert('end',f"\nRESULT // {msg}\n")
            state.configure(state='disabled')
        def propose():
            c=propose_from_learning(self.brain); refresh(f"Candidate proposed: {c['changes']}")
        def promote():
            ok,msg=promote_latest(); refresh(msg)
        def rollback():
            ok,msg=rollback_generation(); refresh(msg)
        refresh(); row=ctk.CTkFrame(w,fg_color='transparent'); row.pack(fill='x',padx=22)
        ctk.CTkButton(row,text='PROPOSE',command=propose,fg_color=PANEL,border_width=1,border_color=LINE).pack(side='left',padx=(0,8))
        ctk.CTkButton(row,text='PROMOTE',command=promote,fg_color=RED_DARK,border_width=1,border_color=RED).pack(side='left',padx=8)
        ctk.CTkButton(row,text='ROLLBACK',command=rollback,fg_color='transparent',border_width=1,border_color=AMBER,text_color=AMBER).pack(side='left',padx=8)
        ctk.CTkButton(row,text='CLOSE',command=w.destroy,fg_color='transparent',border_width=1,border_color=LINE).pack(side='right')
    app_cls.__init__=init; app_cls._open_evolution_v11=open_evo; app_cls._evolution_ui_v11=True