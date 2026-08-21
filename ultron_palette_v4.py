from __future__ import annotations
import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; LINE="#381017"; RED="#FF3045"; RED_DARK="#410811"; WHITE="#F7F7FA"; MUTED="#7D7D88"

COMMANDS=[
("Open Brain","brain"),("Control Center","center"),("Analyze Screen","look at my screen"),("Test NVIDIA","test nvidia"),("System Scan","ultron status"),("Memory","what do you remember"),("Focus Mode","focus mode"),("Performance Mode","performance mode"),("Check Updates","check for updates"),("Update ULTRON","update ultron")]

def install_palette_v4(app_cls):
    if getattr(app_cls,"_palette_v4",False): return
    old=app_cls.__init__
    def init(self,*a,**k):
        old(self,*a,**k); self._mini=None
        self.bind("<Control-k>",lambda _e:self._open_palette_v4())
    def palette(self):
        win=ctk.CTkToplevel(self); win.title("ULTRON // Command Palette"); win.geometry("560x470"); win.configure(fg_color=VOID); win.transient(self); win.grab_set()
        q=ctk.CTkEntry(win,placeholder_text="Search commands...",height=42,fg_color=PANEL,border_width=1,border_color=RED,text_color=WHITE); q.pack(fill="x",padx=18,pady=18); frame=ctk.CTkScrollableFrame(win,fg_color=VOID); frame.pack(fill="both",expand=True,padx=12,pady=(0,12))
        def execute(cmd):
            win.destroy()
            if cmd=="brain": self.open_brain()
            elif cmd=="center": self.open_control_center()
            else: self._quick(cmd)
        def render(*_):
            for w in frame.winfo_children(): w.destroy()
            needle=q.get().lower().strip()
            for label,cmd in COMMANDS:
                if needle and needle not in label.lower() and needle not in cmd.lower(): continue
                ctk.CTkButton(frame,text=label,anchor="w",height=36,fg_color=PANEL,hover_color=RED_DARK,border_width=1,border_color=LINE,text_color=WHITE,command=lambda c=cmd:execute(c)).pack(fill="x",pady=3)
        q.bind("<KeyRelease>",render); render(); q.focus_force()
    def mini(self):
        if self._mini and self._mini.winfo_exists(): self._mini.lift(); return
        w=ctk.CTkToplevel(self); self._mini=w; w.title("ULTRON MINI"); w.geometry("280x88+40+40"); w.configure(fg_color=VOID); w.attributes("-topmost",True); w.overrideredirect(True)
        shell=ctk.CTkFrame(w,fg_color=PANEL,corner_radius=22,border_width=1,border_color=RED); shell.pack(fill="both",expand=True,padx=3,pady=3)
        ctk.CTkLabel(shell,text="◉",font=ctk.CTkFont("Segoe UI",28,"bold"),text_color=RED).pack(side="left",padx=(16,8))
        ctk.CTkLabel(shell,text="ULTRON\nPRIME CORE",justify="left",font=ctk.CTkFont("Consolas",9,"bold"),text_color=WHITE).pack(side="left")
        ctk.CTkButton(shell,text="MIC",width=50,command=self._start_listen_once,fg_color=RED_DARK).pack(side="right",padx=4)
        ctk.CTkButton(shell,text="×",width=34,command=w.destroy,fg_color="transparent",hover_color=RED_DARK).pack(side="right",padx=(0,10))
        shell.bind("<Double-Button-1>",lambda _e:self._show_from_tray())
    app_cls.__init__=init; app_cls._open_palette_v4=palette; app_cls._open_mini_v4=mini; app_cls._palette_v4=True