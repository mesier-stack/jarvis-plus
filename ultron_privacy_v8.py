from __future__ import annotations
import os
from pathlib import Path
import customtkinter as ctk
VOID='#020203';PANEL='#08080B';LINE='#381017';RED='#FF3045';WHITE='#F7F7FA';MUTED='#7D7D88';GREEN='#59F6A3'
def install_privacy_v8(app_cls):
    if getattr(app_cls,'_privacy_v8',False): return
    old=app_cls.__init__
    def init(self,*a,**k): old(self,*a,**k);self.bind('<Control-Shift-P>',lambda _e:self._privacy_v8())
    def show(self):
        w=ctk.CTkToplevel(self);w.title('ULTRON // Privacy');w.geometry('720x590');w.configure(fg_color=VOID);w.transient(self)
        ctk.CTkLabel(w,text='PRIVACY CORE',font=ctk.CTkFont('Segoe UI',27,'bold'),text_color=WHITE).pack(anchor='w',padx=22,pady=(20,2));ctk.CTkLabel(w,text='DATA / KEYS / LOCAL STORAGE',font=ctk.CTkFont('Consolas',9,'bold'),text_color=RED).pack(anchor='w',padx=22)
        body=ctk.CTkFrame(w,fg_color=PANEL,border_width=1,border_color=LINE);body.pack(fill='both',expand=True,padx=22,pady=18)
        data=Path(os.getenv('APPDATA',Path.home()))/'ULTRON'; rows=[('NVIDIA KEY','CONFIGURED' if os.getenv('NVIDIA_API_KEY') else 'NOT SET'),('KEY DISPLAY','NEVER SHOWN'),('MEMORY STORAGE',str(data)),('VISION','ON DEMAND'),('CAMERA','NOT REQUIRED'),('ACTION PERMISSIONS','GATED')]
        for n,v in rows:
            r=ctk.CTkFrame(body,fg_color='transparent');r.pack(fill='x',padx=14,pady=8);ctk.CTkLabel(r,text=n,text_color=MUTED,font=ctk.CTkFont('Consolas',9)).pack(side='left');ctk.CTkLabel(r,text=v,text_color=GREEN if v in {'CONFIGURED','NEVER SHOWN','ON DEMAND','NOT REQUIRED','GATED'} else WHITE,font=ctk.CTkFont('Consolas',9,'bold')).pack(side='right')
    app_cls.__init__=init;app_cls._privacy_v8=show;app_cls._privacy_v8_installed=True