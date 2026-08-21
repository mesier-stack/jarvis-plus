from __future__ import annotations

import math
import os
import random
import tkinter as tk
import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; PANEL2="#0D0D12"; LINE="#381017"; LINE_HI="#8F1C2B"; RED="#FF3045"; RED_DARK="#410811"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"; AMBER="#FFBE63"

class BrainV3(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app); self.app=app; self.title("ULTRON // Neural Galaxy"); self.geometry("1380x840"); self.minsize(1100,700); self.configure(fg_color=VOID); self.transient(app)
        self.phase=0.0; self.selected="core"; self.positions={}; self.particles=[(random.random(),random.random(),random.random()*6.28) for _ in range(140)]
        self.nodes={
            "core":("PRIME CORE","Cognition, routing and global state",0,0),"nvidia":("NEMOTRON","Primary reasoning provider",1,0),"vision":("VISION","Screen understanding and visual context",1,60),"voice":("VOICE","Speech input, synthesis and interruption",1,120),"memory":("MEMORY","Private persistent context",1,180),"actions":("ACTIONS","Permission-gated Windows control",1,240),"planner":("PLANNER","Task decomposition and execution planning",1,300),
            "router":("AI ROUTER","Intent classification and provider selection",2,20),"files":("FILES","Local file intelligence",2,60),"language":("ES / EN","Automatic bilingual handling",2,100),"permissions":("PERMISSIONS","ALLOW / ASK / DENY policy",2,140),"recovery":("RECOVERY","Fault containment and module health",2,180),"watch":("WATCH","Explicit local condition monitoring",2,220),"telemetry":("TELEMETRY","CPU, RAM, disk, network and GPU",2,260),"skills":("SKILLS","Capability registry",2,300),"updates":("UPDATER","Signed source refresh and restart",2,340),
        }
        self.links=[("core",x) for x in ("nvidia","vision","voice","memory","actions","planner")]+[("nvidia","router"),("router","language"),("vision","telemetry"),("vision","permissions"),("voice","language"),("memory","files"),("actions","permissions"),("planner","files"),("planner","skills"),("recovery","core"),("watch","telemetry"),("updates","core"),("skills","actions")]
        self.grid_columnconfigure(0,weight=1); self.grid_columnconfigure(1,weight=0); self.grid_rowconfigure(1,weight=1)
        self._header(); self._network(); self._panel(); self.after(25,self._animate); self.after(800,self._refresh)

    def _header(self):
        h=ctk.CTkFrame(self,height=78,fg_color=VOID,corner_radius=0); h.grid(row=0,column=0,columnspan=2,sticky="ew",padx=18,pady=(10,0)); h.grid_columnconfigure(1,weight=1); h.grid_propagate(False)
        ctk.CTkLabel(h,text="ULTRON // NEURAL GALAXY",font=ctk.CTkFont("Segoe UI",26,"bold"),text_color=WHITE).grid(row=0,column=0,sticky="w",padx=8)
        self.state=ctk.CTkLabel(h,text="COGNITION // STANDBY",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED); self.state.grid(row=0,column=1)
        ctk.CTkButton(h,text="CLOSE",command=self.destroy,width=82,fg_color="transparent",hover_color=RED_DARK,border_width=1,border_color=LINE_HI).grid(row=0,column=2,padx=8)
    def _network(self):
        f=ctk.CTkFrame(self,fg_color=PANEL,corner_radius=12,border_width=1,border_color=LINE); f.grid(row=1,column=0,sticky="nsew",padx=(18,8),pady=12); f.grid_rowconfigure(1,weight=1); f.grid_columnconfigure(0,weight=1)
        t=ctk.CTkFrame(f,height=44,fg_color=PANEL2,corner_radius=12); t.grid(row=0,column=0,sticky="ew",padx=1,pady=1); t.grid_propagate(False)
        ctk.CTkLabel(t,text="LIVE COGNITIVE TOPOLOGY",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED).pack(side="left",padx=14)
        self.stats=ctk.CTkLabel(t,text="",font=ctk.CTkFont("Consolas",8),text_color=MUTED); self.stats.pack(side="right",padx=14)
        self.canvas=tk.Canvas(f,bg=VOID,highlightthickness=0); self.canvas.grid(row=1,column=0,sticky="nsew",padx=2,pady=(0,2)); self.canvas.bind("<Button-1>",self._click)
    def _panel(self):
        p=ctk.CTkFrame(self,width=330,fg_color=PANEL,corner_radius=12,border_width=1,border_color=LINE); p.grid(row=1,column=1,sticky="nsew",padx=(8,18),pady=12); p.grid_propagate(False)
        ctk.CTkLabel(p,text="NODE INSPECTOR",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED).pack(anchor="w",padx=16,pady=(18,5))
        self.name=ctk.CTkLabel(p,text="PRIME CORE",font=ctk.CTkFont("Segoe UI",24,"bold"),text_color=WHITE,wraplength=290,justify="left"); self.name.pack(anchor="w",padx=16,pady=(7,2))
        self.status=ctk.CTkLabel(p,text="ONLINE",font=ctk.CTkFont("Consolas",10,"bold"),text_color=GREEN); self.status.pack(anchor="w",padx=16)
        self.desc=ctk.CTkLabel(p,text="Cognition, routing and global state",font=ctk.CTkFont("Consolas",9),text_color=MUTED,wraplength=290,justify="left"); self.desc.pack(anchor="w",padx=16,pady=(12,18))
        self.live=ctk.CTkTextbox(p,height=330,fg_color="#050507",border_width=1,border_color=LINE,text_color=WHITE,font=ctk.CTkFont("Consolas",9)); self.live.pack(fill="x",padx=14); self.live.configure(state="disabled")
        ctk.CTkLabel(p,text="COGNITIVE LOAD",font=ctk.CTkFont("Consolas",9,"bold"),text_color=RED).pack(anchor="w",padx=16,pady=(18,7))
        self.bar=ctk.CTkProgressBar(p,height=8,fg_color=LINE,progress_color=RED); self.bar.pack(fill="x",padx=16); self.bar.set(.15)
        self.percent=ctk.CTkLabel(p,text="15%",font=ctk.CTkFont("Consolas",8),text_color=MUTED); self.percent.pack(anchor="e",padx=16,pady=5)
    def _status_map(self):
        b=self.app.brain; provider=getattr(b.ai,"provider","local"); ai=getattr(b.ai,"available",False); voice=getattr(self.app.voice,"available",False)
        return {"core":(True,"ONLINE"),"nvidia":(provider=="nvidia","ONLINE" if provider=="nvidia" else provider.upper()),"vision":(True,"READY"),"voice":(voice,"ONLINE" if voice else "OFFLINE"),"memory":(True,f"{len(b.memory.list_memories(99))} ITEMS"),"actions":(os.name=="nt","ARMED"),"planner":(True,"READY"),"router":(True,provider.upper()),"files":(True,"READY"),"language":(True,"ES / EN AUTO"),"permissions":(True,"ARMED"),"recovery":(True,"ONLINE"),"watch":(True,"STANDBY"),"telemetry":(True,"LIVE"),"skills":(True,"ONLINE"),"updates":(True,"READY")}
    def _refresh(self):
        s=self._status_map(); lines=[]
        for k,(label,_,_,_) in self.nodes.items():
            ok,st=s.get(k,(False,"UNKNOWN")); lines.append(f"{'●' if ok else '○'} {label:<16} {st}")
        self.live.configure(state="normal"); self.live.delete("1.0","end"); self.live.insert("end","\n".join(lines)); self.live.configure(state="disabled"); self.after(1200,self._refresh)
    def _click(self,e):
        best=None
        for k,(x,y) in self.positions.items():
            d=math.hypot(e.x-x,e.y-y)
            if best is None or d<best[0]: best=(d,k)
        if best and best[0]<38:
            self.selected=best[1]; label,desc,_,_=self.nodes[self.selected]; ok,st=self._status_map().get(self.selected,(False,"UNKNOWN")); self.name.configure(text=label); self.desc.configure(text=desc); self.status.configure(text=st,text_color=GREEN if ok else AMBER)
    def _animate(self):
        c=self.canvas; w=max(c.winfo_width(),10); h=max(c.winfo_height(),10); c.delete("all"); cx,cy=w/2,h/2
        for i,(x,y,p) in enumerate(self.particles):
            rr=1 if i%5 else 2; glow=(math.sin(self.phase+p)+1)/2; c.create_oval(x*w-rr,y*h-rr,x*w+rr,y*h+rr,fill="#321017" if glow>.62 else "#16090C",outline="")
        r1=min(w,h)*.22; r2=min(w,h)*.39; self.positions={}
        for r,col in ((r1,"#351017"),(r2,"#261014"),(r2*1.07,"#16090C")): c.create_oval(cx-r,cy-r,cx+r,cy+r,outline=col)
        for k,(label,desc,ring,ang) in self.nodes.items():
            if ring==0: x,y=cx,cy
            else:
                r=r1 if ring==1 else r2; a=math.radians(ang+math.sin(self.phase+ang)*1.3); x=cx+math.cos(a)*r; y=cy+math.sin(a)*r
            self.positions[k]=(x,y)
        active=1.0 if self.app.processing else (.72 if self.app.listening else .18)
        for i,(a,b) in enumerate(self.links):
            x1,y1=self.positions[a]; x2,y2=self.positions[b]; hot=(math.sin(self.phase*2+i*.8)+1)/2>.72 and active>.35
            c.create_line(x1,y1,x2,y2,fill=RED if hot else "#351017",width=2 if hot else 1)
            if hot:
                t=(self.phase*.55+i*.13)%1; x=x1+(x2-x1)*t; y=y1+(y2-y1)*t; c.create_oval(x-2,y-2,x+2,y+2,fill=RED,outline="")
        st=self._status_map()
        for k,(label,desc,ring,ang) in self.nodes.items():
            x,y=self.positions[k]; ok,_=st.get(k,(False,"UNKNOWN")); sel=k==self.selected
            if k=="core":
                s=30+math.sin(self.phase*2)*4+active*5; c.create_oval(x-s,y-s,x+s,y+s,fill=RED_DARK,outline=RED,width=3); c.create_oval(x-10,y-10,x+10,y+10,fill=RED,outline="")
            else:
                s=9 if ring==1 else 6; fill=GREEN if ok else AMBER
                if sel: c.create_oval(x-s-8,y-s-8,x+s+8,y+s+8,outline=RED,width=2)
                c.create_oval(x-s,y-s,x+s,y+s,fill=fill,outline=WHITE if ring==1 else "")
            if ring==1 or sel: c.create_text(x,y+20,text=label,fill=WHITE if sel else MUTED,font=("Consolas",7,"bold" if sel else "normal"))
        pct=int(active*100); self.bar.set(active); self.percent.configure(text=f"{pct}%"); self.state.configure(text="COGNITION // ACTIVE" if self.app.processing else ("AUDIO // LISTENING" if self.app.listening else "COGNITION // STANDBY"),text_color=AMBER if self.app.processing else (GREEN if self.app.listening else RED)); self.stats.configure(text=f"NODES {len(self.nodes)}  //  LINKS {len(self.links)}  //  ACTIVITY {pct}%")
        self.phase+=.055; self.after(30,self._animate)

def install_brain_ui_v3(app_cls):
    if getattr(app_cls,"_brain_ui_v3_installed",False): return
    original_init=app_cls.__init__
    def init(self,*a,**kw):
        original_init(self,*a,**kw); self._brain_v3=None
        def open_brain():
            cur=getattr(self,"_brain_v3",None)
            try:
                if cur is not None and cur.winfo_exists(): cur.lift(); cur.focus_force(); return
            except Exception: pass
            self._brain_v3=BrainV3(self)
        self.open_brain=open_brain; self.bind("<Control-b>",lambda _e:open_brain())
        ctk.CTkButton(self,text="BRAIN",command=open_brain,width=88,height=32,corner_radius=8,fg_color=RED_DARK,hover_color="#7A1421",border_width=1,border_color=RED,text_color=WHITE,font=ctk.CTkFont("Consolas",9,"bold")).place(relx=.5,y=24,anchor="n")
    app_cls.__init__=init; app_cls._brain_ui_v3_installed=True
