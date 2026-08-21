from __future__ import annotations
import os,time
import customtkinter as ctk
RED='#FF3045';GREEN='#59F6A3';MUTED='#7D7D88';PANEL='#08080B'
def install_status_strip_v7(app_cls):
    if getattr(app_cls,'_status_strip_v7',False): return
    old=app_cls.__init__
    def init(self,*a,**k):
        old(self,*a,**k)
        try:
            bar=ctk.CTkFrame(self,height=24,corner_radius=0,fg_color=PANEL);bar.place(relx=0,rely=1,anchor='sw',relwidth=1);bar.lift();self._v7_strip=ctk.CTkLabel(bar,text='',font=ctk.CTkFont('Consolas',8,'bold'),text_color=MUTED);self._v7_strip.pack(side='left',padx=10);self.after(500,self._tick_strip_v7)
        except Exception: pass
    def tick(self):
        try:
            state='THINKING' if self.processing else ('LISTENING' if self.listening else 'READY');ai=getattr(self.brain.ai,'provider','local').upper();key='KEY OK' if os.getenv('NVIDIA_API_KEY') else 'NO KEY';profile=self.brain.memory.get_setting('ultron_profile','balanced').upper();self._v7_strip.configure(text=f'● {state}   AI:{ai}   {key}   PROFILE:{profile}   {time.strftime("%H:%M:%S")}',text_color=RED if state!='READY' else GREEN);self.after(1000,self._tick_strip_v7)
        except Exception: pass
    app_cls.__init__=init;app_cls._tick_strip_v7=tick;app_cls._status_strip_v7=True