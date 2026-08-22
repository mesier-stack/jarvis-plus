from __future__ import annotations
import math,time,tkinter as tk
import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; LINE="#381017"; RED="#FF3045"; RED_DARK="#410811"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"

def install_home_v5(app_cls):
    if getattr(app_cls,"_home_v5",False): return
    old=app_cls.__init__
    def init(self,*a,**k):
        self._v3_started=time.monotonic()
        old(self,*a,**k)
        self.bind("<Control-h>",lambda _e:self._open_home_v5())
    def open_home(self):
        w=ctk.CTkToplevel(self); w.title("ULTRON // Home"); w.geometry("1100x700"); w.configure(fg_color=VOID); w.transient(self)
        head=ctk.CTkFrame(w,fg_color=VOID); head.pack(fill="x",padx=24,pady=(20,8)); ctk.CTkLabel(head,text="ULTRON // HOME",font=ctk.CTkFont("Segoe UI",28,"bold"),text_color=WHITE).pack(side="left"); ctk.CTkLabel(head,text="CORE ONLINE",font=ctk.CTkFont("Consolas",9,"bold"),text_color=GREEN).pack(side="right")
        body=ctk.CTkFrame(w,fg_color="transparent"); body.pack(fill="both",expand=True,padx=24,pady=(0,24)); body.grid_columnconfigure((0,1,2),weight=1); body.grid_rowconfigure(0,weight=1)
        cards=[]
        for i in range(3):
            f=ctk.CTkFrame(body,fg_color=PANEL,corner_radius=12,border_width=1,border_color=LINE); f.grid(row=0,column=i,sticky="nsew",padx=5); cards.append(f)
        ctk.CTkLabel(cards[0],text="PRIME CORE",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED).pack(anchor="w",padx=14,pady=(14,6)); canvas=tk.Canvas(cards[0],bg=VOID,highlightthickness=0,height=300); canvas.pack(fill="both",expand=True,padx=10,pady=10)
        ctk.CTkLabel(cards[1],text="SESSION",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED).pack(anchor="w",padx=14,pady=(14,6)); stats=ctk.CTkLabel(cards[1],text="",justify="left",font=ctk.CTkFont("Consolas",10),text_color=WHITE); stats.pack(anchor="nw",padx=14,pady=12)
        ctk.CTkLabel(cards[2],text="QUICK ACCESS",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED).pack(anchor="w",padx=14,pady=(14,8))

        def optional(method,*fallback):
            def call():
                fn=getattr(self,method,None)
                if callable(fn): return fn()
                if fallback and callable(fallback[0]): return fallback[0]()
            return call

        entries=[
            ("BRAIN",optional("open_brain")),
            ("CONTROL CENTER",optional("open_control_center")),
            ("COMMAND PALETTE",optional("_open_palette_v4")),
            ("DIAGNOSTICS",optional("_open_diag_v5")),
            ("MEMORY",optional("open_memory_center",lambda:self._quick("what do you remember"))),
            ("VISION",optional("open_vision_center",lambda:self._quick("look at my screen"))),
        ]
        for label,fn in entries:
            ctk.CTkButton(cards[2],text=label,command=fn,height=36,fg_color="#0D0D12",hover_color=RED_DARK,border_width=1,border_color=LINE).pack(fill="x",padx=12,pady=4)

        phase=[0.0]
        def tick():
            try:
                if not w.winfo_exists(): return
                canvas.delete("all"); ww=max(canvas.winfo_width(),2); hh=max(canvas.winfo_height(),2); cx,cy=ww/2,hh/2; r=min(ww,hh)*.23; p=phase[0]
                for s,col in ((1.7,"#1A0A0D"),(1.42,"#4B1119"),(1.12,RED)):
                    rr=r*s; canvas.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline=col,width=2 if s<1.5 else 1)
                for i in range(18):
                    a=p+i*math.tau/18; rr=r*1.55; x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr; canvas.create_oval(x-2,y-2,x+2,y+2,fill=RED,outline="")
                canvas.create_oval(cx-r*.45,cy-r*.45,cx+r*.45,cy+r*.45,fill=RED_DARK,outline=RED,width=3); canvas.create_text(cx,cy,text="ULTRON",fill=WHITE,font=("Consolas",13,"bold")); phase[0]+=0.02
                uptime=int(time.monotonic()-getattr(self,"_v3_started",time.monotonic())); provider=getattr(getattr(self.brain,"ai",None),"provider","local").upper(); profile=self.brain.memory.get_setting("ultron_profile","balanced").upper()
                try: memories=len(self.brain.memory.list_memories(99))
                except Exception: memories=0
                stats.configure(text=f"UPTIME // {uptime}s\nAI // {provider}\nPROFILE // {profile}\nMEMORIES // {memories}\nSTATE // {'THINKING' if getattr(self,'processing',False) else 'READY'}")
                w.after(40,tick)
            except Exception: pass
        tick()
    app_cls.__init__=init; app_cls._open_home_v5=open_home; app_cls._home_v5=True
