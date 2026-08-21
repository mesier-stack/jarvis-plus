from __future__ import annotations

import time
from collections import deque
import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; LINE="#381017"; RED="#FF3045"; RED_DARK="#410811"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"; AMBER="#FFBE63"
_EVENTS=deque(maxlen=160)

def _push(stage,detail=""):
    _EVENTS.appendleft((time.strftime("%H:%M:%S"),stage,detail[:100]))

def install_neural_timeline_v4(app_cls):
    if getattr(app_cls,"_neural_timeline_v4",False): return
    old_init=app_cls.__init__; old_dispatch=app_cls._dispatch; old_process=app_cls._process; old_handle=app_cls._handle_reply; old_listen=app_cls._start_listen_once
    def init(self,*a,**k):
        old_init(self,*a,**k); self._timeline_win=None
        try: self._top_button(self.wake_btn.master,"TRACE",self._open_timeline_v4).pack(side="left",padx=3)
        except Exception: pass
    def listen(self):
        _push("VOICE","microphone input opened"); return old_listen(self)
    def dispatch(self,text):
        _push("INPUT",text); _push("LANGUAGE","auto ES/EN detect"); _push("ROUTER","classifying directive")
        if any(x in text.lower() for x in ("screen","pantalla","vision","look")): _push("VISION","screen context requested")
        if any(x in text.lower() for x in ("remember","recuerda","memory","memoria")): _push("MEMORY","memory retrieval")
        return old_dispatch(self,text)
    def process(self,text):
        provider=getattr(self.brain.ai,"provider","local").upper(); _push("AI",provider); return old_process(self,text)
    def handle(self,reply):
        _push("OUTPUT",getattr(reply,"kind","answer")); result=old_handle(self,reply)
        if getattr(self,"voice_enabled",False): _push("VOICE","speech output queued")
        return result
    def open_timeline(self):
        if self._timeline_win and self._timeline_win.winfo_exists(): self._timeline_win.lift(); return
        win=ctk.CTkToplevel(self); self._timeline_win=win; win.title("ULTRON // Neural Activity Timeline"); win.geometry("860x610"); win.configure(fg_color=VOID); win.transient(self)
        ctk.CTkLabel(win,text="NEURAL ACTIVITY TIMELINE",font=ctk.CTkFont("Segoe UI",25,"bold"),text_color=WHITE).pack(anchor="w",padx=22,pady=(20,2))
        ctk.CTkLabel(win,text="Live execution path // INPUT → ROUTER → MODULES → AI → OUTPUT",font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(anchor="w",padx=22)
        box=ctk.CTkTextbox(win,fg_color=PANEL,border_width=1,border_color=LINE,text_color=WHITE,font=ctk.CTkFont("Consolas",10)); box.pack(fill="both",expand=True,padx=22,pady=18)
        def refresh():
            if not win.winfo_exists(): return
            box.configure(state="normal"); box.delete("1.0","end")
            for stamp,stage,detail in list(_EVENTS)[:90]: box.insert("end",f"[{stamp}]  {stage:<10}  {detail}\n")
            box.configure(state="disabled"); win.after(350,refresh)
        refresh()
    app_cls.__init__=init; app_cls._dispatch=dispatch; app_cls._process=process; app_cls._handle_reply=handle; app_cls._start_listen_once=listen; app_cls._open_timeline_v4=open_timeline; app_cls._neural_timeline_v4=True
