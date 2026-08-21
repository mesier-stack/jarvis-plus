from __future__ import annotations

import math
import random
import time
import tkinter as tk
from collections import deque
from dataclasses import dataclass

import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; PANEL2="#0D0D12"; LINE="#381017"; LINE_HI="#8F1C2B"; RED="#FF3045"; RED_DARK="#410811"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"; AMBER="#FFBE63"

@dataclass
class Node:
    key:str; label:str; x:float; y:float; group:str; desc:str

class BrainV4(ctk.CTkToplevel):
    def __init__(self,app):
        super().__init__(app); self.app=app; self.title("ULTRON // BRAIN SCREEN 4.0"); self.geometry("1380x850"); self.minsize(1050,680); self.configure(fg_color=VOID); self.transient(app)
        self.zoom=1.0; self.pan_x=0.0; self.pan_y=0.0; self.drag=None; self.phase=0.0; self.selected="core"; self.positions={}; self.timeline=deque(maxlen=18); self._last_state="READY"
        self.nodes=self._nodes(); self.links=self._links(); self.grid_columnconfigure(0,weight=1); self.grid_columnconfigure(1,weight=0); self.grid_rowconfigure(1,weight=1)
        self._header(); self._network(); self._inspector(); self.after(30,self._animate); self.after(200,self._poll)
    def _nodes(self):
        return [Node("core","PRIME CORE",0,0,"core","Central orchestration and cognition."),Node("router","ROUTER",-1.2,-.25,"logic","Routes directives into modules."),Node("language","ES / EN",-1.15,.65,"logic","Automatic bilingual interpretation."),Node("memory","MEMORY",-.55,-1.0,"data","Persistent local memory bank."),Node("vision","VISION",.55,-1.0,"sense","On-demand screen perception."),Node("voice","VOICE",1.2,-.25,"sense","Speech input and output."),Node("nvidia","NEMOTRON",1.15,.65,"ai","NVIDIA NIM reasoning provider."),Node("planner",.55,1.1,"logic","Multi-step plan construction."),Node("actions",-.55,1.1,"action","Permission-gated Windows actions."),Node("permissions",-1.8,1.1,"guard","Confirmation and risk gate."),Node("files",-1.8,-1.05,"data","File discovery and local context."),Node("recovery",1.8,-1.05,"guard","Fault isolation and recovery."),Node("updater",1.8,1.1,"system","Update, backup and rollback."),Node("skills",0,1.75,"system","Safe skill manifest registry."),Node("telemetry",0,-1.7,"system","CPU, RAM and runtime metrics.")]
    def _links(self):
        return [("core",k) for k in ("router","memory","vision","voice","nvidia","planner","actions")]+[("router","language"),("router","nvidia"),("memory","files"),("vision","nvidia"),("voice","language"),("planner","actions"),("actions","permissions"),("core","recovery"),("core","updater"),("core","skills"),("core","telemetry")]
    def _header(self):
        h=ctk.CTkFrame(self,height=76,fg_color=VOID,corner_radius=0); h.grid(row=0,column=0,columnspan=2,sticky="ew",padx=16,pady=(8,0)); h.grid_columnconfigure(1,weight=1); h.grid_propagate(False)
        ctk.CTkLabel(h,text="ULTRON // BRAIN SCREEN 4.0",font=ctk.CTkFont("Segoe UI",25,"bold"),text_color=WHITE).grid(row=0,column=0,sticky="w",padx=8)
        self.state=ctk.CTkLabel(h,text="COGNITION // READY",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED); self.state.grid(row=0,column=1)
        ctk.CTkButton(h,text="RESET VIEW",width=95,command=self._reset,fg_color="transparent",border_width=1,border_color=LINE_HI).grid(row=0,column=2,padx=4)
        ctk.CTkButton(h,text="CLOSE",width=75,command=self.destroy,fg_color="transparent",border_width=1,border_color=LINE_HI).grid(row=0,column=3,padx=4)
    def _network(self):
        f=ctk.CTkFrame(self,fg_color=PANEL,corner_radius=10,border_width=1,border_color=LINE); f.grid(row=1,column=0,sticky="nsew",padx=(16,8),pady=12); f.grid_rowconfigure(1,weight=1); f.grid_columnconfigure(0,weight=1)
        top=ctk.CTkFrame(f,height=38,fg_color=PANEL2,corner_radius=9); top.grid(row=0,column=0,sticky="ew",padx=1,pady=1); top.grid_propagate(False)
        ctk.CTkLabel(top,text="LIVE NEURAL TOPOLOGY",font=ctk.CTkFont("Consolas",9,"bold"),text_color=RED).pack(side="left",padx=12)
        self.stats=ctk.CTkLabel(top,text="",font=ctk.CTkFont("Consolas",8),text_color=MUTED); self.stats.pack(side="right",padx=12)
        self.canvas=tk.Canvas(f,bg=VOID,highlightthickness=0); self.canvas.grid(row=1,column=0,sticky="nsew"); self.canvas.bind("<MouseWheel>",self._wheel); self.canvas.bind("<ButtonPress-1>",self._press); self.canvas.bind("<B1-Motion>",self._drag); self.canvas.bind("<ButtonRelease-1>",self._release)
    def _inspector(self):
        p=ctk.CTkFrame(self,width=330,fg_color=PANEL,corner_radius=10,border_width=1,border_color=LINE); p.grid(row=1,column=1,sticky="nsew",padx=(8,16),pady=12); p.grid_propagate(False)
        ctk.CTkLabel(p,text="NODE INSPECTOR",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED).pack(anchor="w",padx=16,pady=(18,5))
        self.node_name=ctk.CTkLabel(p,text="PRIME CORE",font=ctk.CTkFont("Segoe UI",22,"bold"),text_color=WHITE,wraplength=295,justify="left"); self.node_name.pack(anchor="w",padx=16,pady=(5,2))
        self.node_status=ctk.CTkLabel(p,text="ONLINE",font=ctk.CTkFont("Consolas",10,"bold"),text_color=GREEN); self.node_status.pack(anchor="w",padx=16)
        self.node_desc=ctk.CTkLabel(p,text="Central orchestration and cognition.",font=ctk.CTkFont("Consolas",9),text_color=MUTED,wraplength=295,justify="left"); self.node_desc.pack(anchor="w",padx=16,pady=(10,14))
        ctk.CTkLabel(p,text="NEURAL ACTIVITY TIMELINE",font=ctk.CTkFont("Consolas",9,"bold"),text_color=RED).pack(anchor="w",padx=16,pady=(8,5))
        self.log=ctk.CTkTextbox(p,height=330,fg_color=VOID,border_width=1,border_color=LINE,text_color=WHITE,font=ctk.CTkFont("Consolas",8)); self.log.pack(fill="x",padx=14)
        ctk.CTkLabel(p,text="Mouse wheel = zoom  //  drag = pan",font=ctk.CTkFont("Consolas",8),text_color=MUTED).pack(anchor="w",padx=16,pady=12)
    def _status(self,key):
        if key=="nvidia": return (bool(__import__('os').getenv("NVIDIA_API_KEY")),getattr(self.app.brain.ai,"provider","local").upper())
        if key=="voice": return (bool(getattr(self.app.voice,"available",False)),"ONLINE" if getattr(self.app.voice,"available",False) else "OFFLINE")
        if key=="vision": return (True,getattr(self.app.vision_state,"cget",lambda _k:"READY")("text") if hasattr(self.app,"vision_state") else "READY")
        return (True,"ONLINE")
    def _world(self,n,w,h):
        scale=min(w,h)*.22*self.zoom; return w/2+self.pan_x+n.x*scale,h/2+self.pan_y+n.y*scale
    def _animate(self):
        c=self.canvas; w=max(c.winfo_width(),10); h=max(c.winfo_height(),10); c.delete("all"); self.positions={}
        for i in range(70):
            x=(i*97.3)%w; y=(i*53.7+self.phase*2)%h; c.create_oval(x,y,x+1,y+1,fill="#210B0F",outline="")
        for n in self.nodes: self.positions[n.key]=self._world(n,w,h)
        active=1.0 if self.app.processing else (.75 if self.app.listening else .18)
        for idx,(a,b) in enumerate(self.links):
            x1,y1=self.positions[a]; x2,y2=self.positions[b]; hot=(math.sin(self.phase*.11+idx)+1)/2>.72 and active>.4; c.create_line(x1,y1,x2,y2,fill=RED if hot else "#351016",width=2 if hot else 1)
            if active>.4:
                t=(self.phase*.012+idx*.13)%1; x=x1+(x2-x1)*t; y=y1+(y2-y1)*t; c.create_oval(x-2,y-2,x+2,y+2,fill=RED,outline="")
        for n in self.nodes:
            x,y=self.positions[n.key]; ok,status=self._status(n.key); sel=n.key==self.selected; size=20 if n.key=="core" else 9
            if sel: c.create_oval(x-size-9,y-size-9,x+size+9,y+size+9,outline=RED,width=2)
            fill=RED_DARK if n.key=="core" else (GREEN if ok else AMBER); outline=RED if n.key=="core" else WHITE
            c.create_oval(x-size,y-size,x+size,y+size,fill=fill,outline=outline,width=2 if n.key=="core" else 1)
            if self.zoom>.78 or sel: c.create_text(x,y+size+13,text=n.label,fill=WHITE if sel else MUTED,font=("Consolas",7,"bold" if sel else "normal"))
        self.stats.configure(text=f"ZOOM {self.zoom:.2f}x  //  NODES {len(self.nodes)}  //  LINKS {len(self.links)}"); self.phase+=1; self.after(30,self._animate)
    def _poll(self):
        state="LISTENING" if self.app.listening else ("THINKING" if self.app.processing else ("SPEAKING" if getattr(self.app,"_ultron_speaking",False) else "READY"))
        if state!=self._last_state:
            path={"LISTENING":"VOICE → LANGUAGE → ROUTER","THINKING":"ROUTER → MEMORY → NEMOTRON → PLANNER","SPEAKING":"OUTPUT → VOICE","READY":"CORE → STANDBY"}[state]; self.timeline.appendleft(f"{time.strftime('%H:%M:%S')}  {path}"); self._last_state=state
            self.log.delete("1.0","end"); self.log.insert("end","\n".join(self.timeline))
        self.state.configure(text=f"COGNITION // {state}",text_color=GREEN if state=="LISTENING" else (AMBER if state in ("THINKING","SPEAKING") else RED)); self.after(180,self._poll)
    def _wheel(self,e): self.zoom=max(.45,min(2.4,self.zoom*(1.1 if e.delta>0 else .9)))
    def _press(self,e): self.drag=(e.x,e.y,self.pan_x,self.pan_y); self._maybe_select(e.x,e.y)
    def _drag(self,e):
        if self.drag: sx,sy,px,py=self.drag; self.pan_x=px+e.x-sx; self.pan_y=py+e.y-sy
    def _release(self,_e): self.drag=None
    def _maybe_select(self,x,y):
        if not self.positions:return
        best=min(((math.hypot(x-px,y-py),k) for k,(px,py) in self.positions.items()),default=(999,None))
        if best[0]<30:
            self.selected=best[1]; n=next(n for n in self.nodes if n.key==best[1]); ok,status=self._status(n.key); self.node_name.configure(text=n.label); self.node_status.configure(text=status,text_color=GREEN if ok else AMBER); self.node_desc.configure(text=n.desc)
    def _reset(self): self.zoom=1.0; self.pan_x=0; self.pan_y=0

def install_brain_v4(app_cls):
    if getattr(app_cls,"_brain_v4",False): return
    old=app_cls.__init__
    def init(self,*a,**k):
        old(self,*a,**k); self._brain4=None
        def open_brain():
            if self._brain4 is not None:
                try:
                    if self._brain4.winfo_exists(): self._brain4.lift(); self._brain4.focus_force(); return
                except Exception: pass
            self._brain4=BrainV4(self)
        self.open_brain=open_brain; self.bind("<Control-b>",lambda _e:open_brain())
    app_cls.__init__=init; app_cls._brain_v4=True