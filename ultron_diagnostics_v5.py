from __future__ import annotations
import os, platform, sys, time
from pathlib import Path
import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; LINE="#381017"; RED="#FF3045"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"

def install_diagnostics_v5(app_cls):
    if getattr(app_cls,"_diag_v5",False): return
    old=app_cls.__init__
    def init(self,*a,**k): old(self,*a,**k); self.bind("<Control-d>",lambda _e:self._open_diag_v5())
    def open_diag(self):
        w=ctk.CTkToplevel(self); w.title("ULTRON // Diagnostics"); w.geometry("900x650"); w.configure(fg_color=VOID); w.transient(self)
        ctk.CTkLabel(w,text="DIAGNOSTICS",font=ctk.CTkFont("Segoe UI",28,"bold"),text_color=WHITE).pack(anchor="w",padx=22,pady=(20,0))
        ctk.CTkLabel(w,text="RUNTIME / LOGS / HEALTH",font=ctk.CTkFont("Consolas",9,"bold"),text_color=RED).pack(anchor="w",padx=22)
        stats=ctk.CTkFrame(w,fg_color=PANEL,border_width=1,border_color=LINE); stats.pack(fill="x",padx=22,pady=16)
        provider=getattr(self.brain.ai,"provider","local").upper(); values=[("PYTHON",sys.version.split()[0]),("OS",platform.system()+" "+platform.release()),("AI",provider),("VOICE","READY" if self.voice.available else "LIMITED"),("UPTIME",f"{int(time.monotonic()-getattr(self,'_v3_started',time.monotonic()))}s")]
        for n,v in values: ctk.CTkLabel(stats,text=f"{n}\n{v}",font=ctk.CTkFont("Consolas",9,"bold"),text_color=GREEN if n in {"AI","VOICE"} else WHITE).pack(side="left",expand=True,padx=8,pady=14)
        box=ctk.CTkTextbox(w,fg_color=PANEL,border_width=1,border_color=LINE,text_color=WHITE); box.pack(fill="both",expand=True,padx=22,pady=(0,22))
        log=Path(os.getenv("APPDATA",Path.home()))/"ULTRON"/"logs"/"runtime.log"
        try: text=log.read_text(encoding="utf-8",errors="replace")[-12000:]
        except Exception: text="No runtime faults recorded."
        box.insert("1.0",text); box.configure(state="disabled")
    app_cls.__init__=init; app_cls._open_diag_v5=open_diag; app_cls._diag_v5=True