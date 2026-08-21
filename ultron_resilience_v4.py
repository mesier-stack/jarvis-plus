from __future__ import annotations
import os, time, traceback
from pathlib import Path
import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; LINE="#381017"; RED="#FF3045"; RED_DARK="#410811"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"; AMBER="#FFBE63"

def _log(exc):
    root=Path(os.getenv("APPDATA",Path.home()))/"ULTRON"/"logs"; root.mkdir(parents=True,exist_ok=True); p=root/"runtime.log"
    with p.open("a",encoding="utf-8") as f: f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}]\n{traceback.format_exc()}\n")

def install_resilience_v4(app_cls):
    if getattr(app_cls,"_resilience_v4",False): return
    old_init=app_cls.__init__; old_process=app_cls._process
    def init(self,*a,**k):
        old_init(self,*a,**k)
        if self.brain.memory.get_setting("ultron_first_run_v2","yes")=="yes": self.after(700,self._first_run_v4)
    def process(self,text):
        try: return old_process(self,text)
        except Exception as exc:
            _log(exc); self.inbox.put(("error",f"Module recovered after fault: {exc}"))
    def first_run(self):
        win=ctk.CTkToplevel(self); win.title("ULTRON // Initial Configuration"); win.geometry("700x530"); win.configure(fg_color=VOID); win.transient(self); win.grab_set()
        ctk.CTkLabel(win,text="ULTRON 2.0",font=ctk.CTkFont("Segoe UI",30,"bold"),text_color=WHITE).pack(anchor="w",padx=28,pady=(26,2)); ctk.CTkLabel(win,text="INITIAL SYSTEM CONFIGURATION",font=ctk.CTkFont("Consolas",9,"bold"),text_color=RED).pack(anchor="w",padx=28)
        box=ctk.CTkFrame(win,fg_color=PANEL,corner_radius=12,border_width=1,border_color=LINE); box.pack(fill="both",expand=True,padx=28,pady=22)
        states=[("NVIDIA NEMOTRON","READY" if os.getenv("NVIDIA_API_KEY") else "API KEY MISSING"),("VOICE ENGINE","READY" if self.voice.available else "LIMITED"),("VISION","ON-DEMAND SCREEN MODE"),("LANGUAGE","ES / EN AUTO"),("PERMISSION GATE","ARMED"),("UPDATER","STABLE CHANNEL")]
        for name,state in states:
            r=ctk.CTkFrame(box,fg_color="transparent"); r.pack(fill="x",padx=16,pady=7); ctk.CTkLabel(r,text=name,font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(side="left"); ctk.CTkLabel(r,text=state,font=ctk.CTkFont("Consolas",9,"bold"),text_color=GREEN if "READY" in state or state in ("ARMED","ES / EN AUTO") else AMBER).pack(side="right")
        def done(): self.brain.memory.set_setting("ultron_first_run_v2","done"); win.destroy()
        ctk.CTkButton(win,text="ENTER ULTRON",command=done,height=40,fg_color=RED_DARK,border_width=1,border_color=RED).pack(fill="x",padx=28,pady=(0,26))
    app_cls.__init__=init; app_cls._process=process; app_cls._first_run_v4=first_run; app_cls._resilience_v4=True