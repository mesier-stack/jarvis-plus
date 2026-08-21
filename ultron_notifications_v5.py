from __future__ import annotations
from collections import deque
from datetime import datetime
import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; LINE="#381017"; RED="#FF3045"; WHITE="#F7F7FA"; MUTED="#7D7D88"

def install_notifications_v5(app_cls):
    if getattr(app_cls,"_notifications_v5",False): return
    old_init=app_cls.__init__; old_append=app_cls._append
    def init(self,*a,**k): old_init(self,*a,**k); self._ultron_notifications=deque(maxlen=80); self.bind("<Control-n>",lambda _e:self._open_notifications_v5())
    def append(self,speaker,text,tag="assistant"):
        result=old_append(self,speaker,text,tag)
        if speaker=="SYSTEM" or tag in {"error","status"}: self._ultron_notifications.appendleft((datetime.now().strftime("%H:%M:%S"),speaker,str(text)[:240],tag))
        return result
    def open_notifications(self):
        w=ctk.CTkToplevel(self); w.title("ULTRON // Notifications"); w.geometry("720x580"); w.configure(fg_color=VOID); w.transient(self)
        ctk.CTkLabel(w,text="NOTIFICATION STREAM",font=ctk.CTkFont("Segoe UI",25,"bold"),text_color=WHITE).pack(anchor="w",padx=20,pady=(18,4)); body=ctk.CTkScrollableFrame(w,fg_color=VOID); body.pack(fill="both",expand=True,padx=14,pady=10)
        if not self._ultron_notifications: ctk.CTkLabel(body,text="No system notices yet.",text_color=MUTED).pack(pady=30)
        for t,s,msg,tag in self._ultron_notifications:
            f=ctk.CTkFrame(body,fg_color=PANEL,border_width=1,border_color=RED if tag=="error" else LINE); f.pack(fill="x",pady=4); ctk.CTkLabel(f,text=f"{t} // {s}",font=ctk.CTkFont("Consolas",8,"bold"),text_color=RED).pack(anchor="w",padx=10,pady=(8,2)); ctk.CTkLabel(f,text=msg,wraplength=640,justify="left",text_color=WHITE).pack(anchor="w",padx=10,pady=(0,9))
    app_cls.__init__=init; app_cls._append=append; app_cls._open_notifications_v5=open_notifications; app_cls._notifications_v5=True