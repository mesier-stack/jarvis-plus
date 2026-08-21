from __future__ import annotations

import os
from pathlib import Path

import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; PANEL2="#0D0D12"; LINE="#381017"; RED="#FF3045"; RED_DARK="#410811"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"; AMBER="#FFBE63"


class ControlCenter(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app=app
        self.title("ULTRON // Control Center 2.0")
        self.geometry("1180x760")
        self.minsize(980,650)
        self.configure(fg_color=VOID)
        self.transient(app)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)

        nav=ctk.CTkFrame(self,width=190,corner_radius=0,fg_color=PANEL)
        nav.grid(row=0,column=0,sticky="nsew")
        nav.grid_propagate(False)
        ctk.CTkLabel(nav,text="ULTRON",font=ctk.CTkFont("Segoe UI",25,"bold"),text_color=WHITE).pack(anchor="w",padx=18,pady=(22,2))
        ctk.CTkLabel(nav,text="CONTROL CENTER",font=ctk.CTkFont("Consolas",8,"bold"),text_color=RED).pack(anchor="w",padx=18,pady=(0,18))
        self.content=ctk.CTkFrame(self,fg_color=VOID,corner_radius=0)
        self.content.grid(row=0,column=1,sticky="nsew")
        self.content.grid_columnconfigure(0,weight=1)
        self.content.grid_rowconfigure(1,weight=1)
        for name in ("CORE","AI / NEMOTRON","MEMORY","VISION","VOICE","SYSTEM","SETTINGS"):
            ctk.CTkButton(nav,text=name,anchor="w",height=38,corner_radius=7,fg_color="transparent",hover_color=RED_DARK,text_color=WHITE,font=ctk.CTkFont("Consolas",9,"bold"),command=lambda n=name:self.show(n)).pack(fill="x",padx=10,pady=2)
        ctk.CTkButton(nav,text="CLOSE",command=self.destroy,fg_color="transparent",border_width=1,border_color=LINE).pack(side="bottom",fill="x",padx=12,pady=16)
        self.show("CORE")

    def clear(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def titlebar(self,title,sub):
        h=ctk.CTkFrame(self.content,height=82,fg_color=VOID,corner_radius=0)
        h.grid(row=0,column=0,sticky="ew",padx=24,pady=(12,0))
        h.grid_propagate(False)
        ctk.CTkLabel(h,text=title,font=ctk.CTkFont("Segoe UI",27,"bold"),text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(h,text=sub,font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(anchor="w")

    def show(self,name):
        self.clear()
        self.titlebar(name,"ULTRON // MODULAR SYSTEM CONSOLE")
        pane=ctk.CTkScrollableFrame(self.content,fg_color=PANEL,corner_radius=12,border_width=1,border_color=LINE)
        pane.grid(row=1,column=0,sticky="nsew",padx=24,pady=(0,24))
        handlers={"CORE":self.core,"AI / NEMOTRON":self.ai,"MEMORY":self.memory,"VISION":self.vision,"VOICE":self.voice,"SYSTEM":self.system,"SETTINGS":self.settings}
        handlers.get(name,self.core)(pane)

    def row(self,p,label,value,color=WHITE):
        r=ctk.CTkFrame(p,fg_color=PANEL2,corner_radius=8)
        r.pack(fill="x",padx=10,pady=5)
        ctk.CTkLabel(r,text=label,font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(side="left",padx=12,pady=12)
        ctk.CTkLabel(r,text=str(value),font=ctk.CTkFont("Consolas",9,"bold"),text_color=color).pack(side="right",padx=12)

    def core(self,p):
        self.row(p,"CORE","ONLINE",GREEN)
        self.row(p,"PROVIDER",getattr(getattr(self.app.brain,"ai",None),"provider","local").upper(),RED)
        self.row(p,"MODE","ACTIVE" if getattr(self.app,"processing",False) else "READY")
        self.row(p,"HOTKEY","CTRL + ALT + U")
        self.row(p,"COMMAND PALETTE","CTRL + K")
        ctk.CTkButton(p,text="OPEN NEURAL BRAIN",command=self.app.open_brain,fg_color=RED_DARK,border_width=1,border_color=RED).pack(anchor="w",padx=10,pady=14)

    def ai(self,p):
        model=os.getenv("NVIDIA_MODEL","nvidia/nemotron-3-ultra-550b-a55b")
        self.row(p,"PROVIDER",getattr(getattr(self.app.brain,"ai",None),"provider","local").upper(),RED)
        self.row(p,"MODEL",model)
        has_key=bool(os.getenv("NVIDIA_API_KEY"))
        self.row(p,"API KEY","CONFIGURED" if has_key else "MISSING",GREEN if has_key else AMBER)
        ctk.CTkButton(p,text="RUN LIVE AI HEALTH TEST",command=lambda:self.app._quick("test nvidia"),fg_color=RED_DARK,border_width=1,border_color=RED).pack(anchor="w",padx=10,pady=14)

    def memory(self,p):
        try:
            items=self.app.brain.memory.list_memories(100)
        except Exception:
            items=[]
        self.row(p,"MEMORY ITEMS",len(items),RED)
        box=ctk.CTkTextbox(p,height=320,fg_color=VOID,border_width=1,border_color=LINE,text_color=WHITE)
        box.pack(fill="x",padx=10,pady=10)
        for i,item in enumerate(items,1):
            box.insert("end",f"{i:02d} // {item}\n\n")
        ctk.CTkButton(p,text="ASK ULTRON WHAT IT REMEMBERS",command=lambda:self.app._quick("what do you remember"),fg_color=PANEL2,border_width=1,border_color=LINE).pack(anchor="w",padx=10,pady=8)

    def vision(self,p):
        state="STANDBY"
        try:
            state=self.app.vision_state.cget("text")
        except Exception:
            pass
        self.row(p,"VISION NODE",state,RED)
        self.row(p,"CAMERA","NOT REQUIRED")
        self.row(p,"SCREEN ANALYSIS","ON DEMAND")
        ctk.CTkButton(p,text="ANALYZE CURRENT SCREEN",command=lambda:self.app._quick("look at my screen"),fg_color=RED_DARK,border_width=1,border_color=RED).pack(anchor="w",padx=10,pady=14)

    def voice(self,p):
        voice=getattr(self.app,"voice",None)
        cloud=bool(getattr(voice,"cloud_available",False))
        local=bool(getattr(voice,"available",False))
        self.row(p,"VOICE ENGINE","CLOUD" if cloud else ("LOCAL" if local else "OFFLINE"),RED)
        try:
            lang=self.app.brain.memory.get_setting("voice_language","auto").upper()
        except Exception:
            lang="AUTO"
        self.row(p,"LANGUAGE",lang)
        self.row(p,"STATE","LISTENING" if getattr(self.app,"listening",False) else "READY")
        ctk.CTkButton(p,text="TEST MICROPHONE",command=self.app._start_listen_once,fg_color=PANEL2,border_width=1,border_color=LINE).pack(anchor="w",padx=10,pady=14)

    def system(self,p):
        try:
            import psutil
            disk_root="C:\\" if os.name=="nt" else "/"
            self.row(p,"CPU",f"{psutil.cpu_percent():.0f}%")
            self.row(p,"RAM",f"{psutil.virtual_memory().percent:.0f}%")
            self.row(p,"STORAGE",f"{psutil.disk_usage(disk_root).percent:.0f}%")
        except Exception:
            self.row(p,"TELEMETRY","AVAILABLE IN MAIN CORE")
        self.row(p,"DATA DIRECTORY",Path(os.getenv("APPDATA",str(Path.home())))/"ULTRON")

    def settings(self,p):
        try:
            perf=self.app.brain.memory.get_setting("ultron_performance","off")
            channel=self.app.brain.memory.get_setting("ultron_update_channel","stable")
        except Exception:
            perf="off"; channel="stable"
        self.row(p,"PERFORMANCE MODE",perf.upper())
        self.row(p,"UPDATE CHANNEL",channel.upper())
        self.row(p,"START WITH WINDOWS","MANAGE FROM TRAY")
        ctk.CTkButton(p,text="TOGGLE PERFORMANCE",command=lambda:self.app._quick("performance mode"),fg_color=PANEL2,border_width=1,border_color=LINE).pack(anchor="w",padx=10,pady=8)


def install_control_center_v4(app_cls):
    if getattr(app_cls,"_control_center_v4",False):
        return
    old=app_cls.__init__
    def init(self,*a,**k):
        self._control_center=None
        old(self,*a,**k)
        def open_cc():
            try:
                if self._control_center is not None and self._control_center.winfo_exists():
                    self._control_center.lift(); self._control_center.focus_force(); return
            except Exception:
                self._control_center=None
            self._control_center=ControlCenter(self)
        self.open_control_center=open_cc
        self.bind("<Control-comma>",lambda _e:open_cc())
        try:
            self._top_button(self.wake_btn.master,"CENTER",open_cc).pack(side="left",padx=3)
        except Exception:
            pass
    app_cls.__init__=init
    app_cls._control_center_v4=True
