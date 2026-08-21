from __future__ import annotations
import time
import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; LINE="#381017"; RED="#FF3045"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"

def install_session_analytics_v6(app_cls):
    if getattr(app_cls,"_session_analytics_v6",False): return
    old_init=app_cls.__init__; old_dispatch=app_cls._dispatch; old_assistant=app_cls._assistant
    def init(self,*a,**k):
        # Counters must exist before the base UI emits its startup assistant message.
        self._session_started=time.monotonic()
        self._session_directives=0
        self._session_replies=0
        self._session_voice=0
        self._session_errors=0
        old_init(self,*a,**k)
        self.bind("<Control-Shift-A>",lambda _e:self._open_session_analytics_v6())
    def dispatch(self,text):
        self._session_directives=getattr(self,"_session_directives",0)+1
        return old_dispatch(self,text)
    def assistant(self,text,speak):
        self._session_replies=getattr(self,"_session_replies",0)+1
        if speak: self._session_voice=getattr(self,"_session_voice",0)+1
        if "fault" in str(text).lower() or "failed" in str(text).lower():
            self._session_errors=getattr(self,"_session_errors",0)+1
        return old_assistant(self,text,speak)
    def open_dash(self):
        w=ctk.CTkToplevel(self); w.title("ULTRON // Session Analytics"); w.geometry("780x520"); w.configure(fg_color=VOID); w.transient(self)
        ctk.CTkLabel(w,text="SESSION ANALYTICS",font=ctk.CTkFont("Segoe UI",27,"bold"),text_color=WHITE).pack(anchor="w",padx=22,pady=(20,3)); ctk.CTkLabel(w,text="LIVE RUNTIME METRICS",font=ctk.CTkFont("Consolas",9,"bold"),text_color=RED).pack(anchor="w",padx=22)
        grid=ctk.CTkFrame(w,fg_color=VOID); grid.pack(fill="both",expand=True,padx=18,pady=18)
        def card(title,val,color=WHITE):
            f=ctk.CTkFrame(grid,fg_color=PANEL,border_width=1,border_color=LINE,corner_radius=10); f.pack(fill="x",pady=5); ctk.CTkLabel(f,text=title,font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(side="left",padx=14,pady=14); ctk.CTkLabel(f,text=str(val),font=ctk.CTkFont("Consolas",11,"bold"),text_color=color).pack(side="right",padx=14)
        uptime=int(time.monotonic()-getattr(self,"_session_started",time.monotonic())); card("UPTIME",f"{uptime//60}m {uptime%60}s",GREEN); card("DIRECTIVES",getattr(self,"_session_directives",0),RED); card("RESPONSES",getattr(self,"_session_replies",0)); card("VOICE OUTPUTS",getattr(self,"_session_voice",0)); card("RECOVERED ERRORS",getattr(self,"_session_errors",0))
    app_cls.__init__=init; app_cls._dispatch=dispatch; app_cls._assistant=assistant; app_cls._open_session_analytics_v6=open_dash; app_cls._session_analytics_v6=True