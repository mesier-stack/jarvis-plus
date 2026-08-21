from __future__ import annotations

import math
import random
import tkinter as tk
import customtkinter as ctk

VOID = "#020203"
PANEL = "#08080B"
PANEL_2 = "#0D0D12"
GLASS = "#111117"
LINE = "#391017"
LINE_HI = "#8F1C2B"
RED = "#FF3045"
RED_SOFT = "#B51F31"
RED_DARK = "#410811"
WHITE = "#F7F7FA"
MUTED = "#7D7D88"
GREEN = "#59F6A3"
AMBER = "#FFBE63"


def install_ui_v3(app_cls) -> None:
    if getattr(app_cls, "_ui_v3_installed", False):
        return

    def top_button(self, parent, text: str, command):
        return ctk.CTkButton(parent, text=text, command=command, width=78, height=32,
            corner_radius=7, fg_color="#0B0B0F", hover_color=RED_DARK,
            border_width=1, border_color=LINE_HI, text_color=WHITE,
            font=ctk.CTkFont("Consolas", 8, "bold"))

    def build_header(self):
        top = ctk.CTkFrame(self, height=84, corner_radius=0, fg_color=VOID)
        top.grid(row=0, column=0, sticky="ew", padx=20)
        top.grid_columnconfigure(1, weight=1); top.grid_propagate(False)
        brand = ctk.CTkFrame(top, fg_color="transparent"); brand.grid(row=0,column=0,sticky="w",pady=14)
        ctk.CTkLabel(brand,text="ULTRON",font=ctk.CTkFont("Segoe UI",34,"bold"),text_color=WHITE).pack(side="left")
        ctk.CTkLabel(brand,text="  ◈  PRIME INTELLIGENCE",font=ctk.CTkFont("Consolas",9,"bold"),text_color=RED).pack(side="left",padx=10,pady=(12,0))
        center = ctk.CTkFrame(top,fg_color="transparent"); center.grid(row=0,column=1)
        self.clock = ctk.CTkLabel(center,text="",font=ctk.CTkFont("Consolas",19,"bold"),text_color=WHITE); self.clock.pack()
        self.date_label = ctk.CTkLabel(center,text="",font=ctk.CTkFont("Consolas",8),text_color=MUTED); self.date_label.pack()
        right=ctk.CTkFrame(top,fg_color="transparent"); right.grid(row=0,column=2,sticky="e")
        self.status_badge=ctk.CTkLabel(right,text="  CORE ONLINE  ",height=30,corner_radius=8,fg_color=RED_DARK,text_color=RED,font=ctk.CTkFont("Consolas",9,"bold")); self.status_badge.pack(side="left",padx=5)
        self.mic_btn=self._top_button(right,"MIC",self._start_listen_once); self.mic_btn.pack(side="left",padx=3)
        self.wake_btn=self._top_button(right,"WAKE: OFF",self._toggle_wake_mode); self.wake_btn.pack(side="left",padx=3)
        self.voice_btn=self._top_button(right,"VOICE: ON",self._toggle_voice); self.voice_btn.pack(side="left",padx=3)
        self._top_button(right,"F11",lambda:self._set_fullscreen(not self.fullscreen)).pack(side="left",padx=3)
        self._top_button(right,"EXIT",self._close).pack(side="left",padx=3)

    def metric(self,parent,label:str):
        row=ctk.CTkFrame(parent,fg_color="transparent",height=29); row.pack(fill="x",padx=13); row.pack_propagate(False)
        ctk.CTkLabel(row,text=label,font=ctk.CTkFont("Consolas",8),text_color=MUTED).pack(side="left")
        value=ctk.CTkLabel(row,text="--",font=ctk.CTkFont("Consolas",9,"bold"),text_color=RED); value.pack(side="right")
        return value

    def build_body(self):
        body=ctk.CTkFrame(self,fg_color="transparent"); body.grid(row=1,column=0,sticky="nsew",padx=20,pady=(0,10))
        body.grid_columnconfigure(0,weight=2); body.grid_columnconfigure(1,weight=6); body.grid_columnconfigure(2,weight=4); body.grid_rowconfigure(0,weight=1)
        rail=ctk.CTkFrame(body,fg_color=PANEL,corner_radius=12,border_width=1,border_color=LINE); rail.grid(row=0,column=0,sticky="nsew",padx=(0,10))
        ctk.CTkLabel(rail,text="SYSTEM MATRIX",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED).pack(anchor="w",padx=15,pady=(16,10))
        self.cpu_label=self._metric(rail,"CPU LOAD"); self.ram_label=self._metric(rail,"MEMORY"); self.disk_label=self._metric(rail,"STORAGE")
        self.memory_label=self._metric(rail,"MEMORY BANK"); self.ai_label=self._metric(rail,"AI CORE"); self.voice_state_label=self._metric(rail,"VOICE LINK"); self.focus_label=self._metric(rail,"FOCUS MODE")
        ctk.CTkFrame(rail,height=1,fg_color=LINE).pack(fill="x",padx=13,pady=13)
        ctk.CTkLabel(rail,text="VISION NODE",font=ctk.CTkFont("Consolas",9,"bold"),text_color=RED).pack(anchor="w",padx=15)
        self.vision_state=ctk.CTkLabel(rail,text="STANDBY",font=ctk.CTkFont("Segoe UI",20,"bold"),text_color=WHITE); self.vision_state.pack(anchor="w",padx=15,pady=(2,10))
        for label,cmd in (("SCAN","ultron status"),("VISION","look at my screen"),("NVIDIA TEST","test nvidia"),("MEMORY","what do you remember"),("FOCUS","focus mode")):
            ctk.CTkButton(rail,text=label,command=lambda c=cmd:self._quick(c),height=34,corner_radius=7,fg_color=PANEL_2,hover_color=RED_DARK,border_width=1,border_color=LINE,text_color=WHITE,font=ctk.CTkFont("Consolas",8,"bold")).pack(fill="x",padx=13,pady=3)

        core=ctk.CTkFrame(body,fg_color=PANEL,corner_radius=12,border_width=1,border_color=LINE); core.grid(row=0,column=1,sticky="nsew",padx=(0,10)); core.grid_rowconfigure(1,weight=1); core.grid_columnconfigure(0,weight=1)
        title=ctk.CTkFrame(core,height=44,fg_color=PANEL_2,corner_radius=12); title.grid(row=0,column=0,sticky="ew",padx=1,pady=1); title.grid_propagate(False)
        ctk.CTkLabel(title,text="COGNITIVE REACTOR // LIVE",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED).pack(side="left",padx=15)
        self.mode_label=ctk.CTkLabel(title,text="MODE // READY",font=ctk.CTkFont("Consolas",8,"bold"),text_color=MUTED); self.mode_label.pack(side="right",padx=15)
        self.canvas=tk.Canvas(core,bg=VOID,highlightthickness=0); self.canvas.grid(row=1,column=0,sticky="nsew",padx=2,pady=(0,2))
        self._v3_particles=[{"x":random.random(),"y":random.random(),"vx":random.uniform(-.00035,.00035),"vy":random.uniform(-.00025,.00025),"r":random.choice((1,1,1,2)),"p":random.random()*6.28} for _ in range(165)]

        comms=ctk.CTkFrame(body,fg_color=PANEL,corner_radius=12,border_width=1,border_color=LINE); comms.grid(row=0,column=2,sticky="nsew"); comms.grid_rowconfigure(1,weight=1); comms.grid_columnconfigure(0,weight=1)
        head=ctk.CTkFrame(comms,height=44,fg_color=PANEL_2,corner_radius=12); head.grid(row=0,column=0,sticky="ew",padx=1,pady=1); head.grid_propagate(False)
        ctk.CTkLabel(head,text="COMMUNICATION LINK",font=ctk.CTkFont("Consolas",10,"bold"),text_color=RED).pack(side="left",padx=15)
        self.security_label=ctk.CTkLabel(head,text="SECURE // ARMED",font=ctk.CTkFont("Consolas",8,"bold"),text_color=GREEN); self.security_label.pack(side="right",padx=15)
        self.chat=ctk.CTkTextbox(comms,corner_radius=8,fg_color="#050507",border_width=1,border_color="#201014",text_color=WHITE,font=ctk.CTkFont("Consolas",11),wrap="word"); self.chat.grid(row=1,column=0,sticky="nsew",padx=10,pady=10); self.chat.configure(state="disabled")
        self.confirm_frame=ctk.CTkFrame(comms,height=60,corner_radius=8,fg_color=GLASS,border_width=1,border_color=AMBER); self.confirm_frame.grid(row=2,column=0,sticky="ew",padx=10,pady=(0,10)); self.confirm_frame.grid_columnconfigure(0,weight=1)
        self.confirm_text=ctk.CTkLabel(self.confirm_frame,text="",anchor="w",text_color=AMBER,font=ctk.CTkFont("Consolas",8,"bold")); self.confirm_text.grid(row=0,column=0,padx=10,sticky="ew")
        ctk.CTkButton(self.confirm_frame,text="CONFIRM",width=78,command=self._confirm_pending,fg_color=RED_DARK,hover_color=RED_SOFT,border_width=1,border_color=RED).grid(row=0,column=1,padx=4,pady=9)
        ctk.CTkButton(self.confirm_frame,text="CANCEL",width=68,command=self._cancel_pending,fg_color="transparent",hover_color=PANEL_2,border_width=1,border_color=LINE_HI).grid(row=0,column=2,padx=(0,8),pady=9)
        self.confirm_frame.grid_remove()

    def build_command_bar(self):
        bar=ctk.CTkFrame(self,height=72,corner_radius=12,fg_color=PANEL_2,border_width=1,border_color=LINE); bar.grid(row=2,column=0,sticky="ew",padx=20,pady=(0,20)); bar.grid_columnconfigure(1,weight=1); bar.grid_propagate(False)
        ctk.CTkLabel(bar,text="◈",font=ctk.CTkFont("Segoe UI",18,"bold"),text_color=RED).grid(row=0,column=0,padx=(16,8))
        self.entry=ctk.CTkEntry(bar,placeholder_text="Directive, question, or command...",height=40,corner_radius=9,fg_color="#050507",border_width=1,border_color=LINE_HI,text_color=WHITE,placeholder_text_color=MUTED,font=ctk.CTkFont("Consolas",11)); self.entry.grid(row=0,column=1,sticky="ew",pady=14); self.entry.bind("<Return>",lambda _e:self._submit())
        self.send_btn=ctk.CTkButton(bar,text="EXECUTE",command=self._submit,width=108,height=40,corner_radius=9,fg_color=RED_DARK,hover_color=RED_SOFT,border_width=1,border_color=RED,text_color=WHITE,font=ctk.CTkFont("Consolas",9,"bold")); self.send_btn.grid(row=0,column=2,padx=(12,5))
        self.ptt_btn=ctk.CTkButton(bar,text="TALK",command=self._start_listen_once,width=76,height=40,corner_radius=9,fg_color="transparent",hover_color=RED_DARK,border_width=1,border_color=LINE_HI,text_color=RED,font=ctk.CTkFont("Consolas",9,"bold")); self.ptt_btn.grid(row=0,column=3,padx=(4,12))

    def animate_core(self):
        c=self.canvas; w=max(c.winfo_width(),2); h=max(c.winfo_height(),2); c.delete("all")
        perf=False
        try: perf=self.brain.memory.get_setting("ultron_performance","off")=="on"
        except Exception: pass
        particles=self._v3_particles[::3] if perf else self._v3_particles
        for p in particles:
            p["x"]=(p["x"]+p["vx"])%1; p["y"]=(p["y"]+p["vy"])%1; p["p"]+=.035
            x=p["x"]*w; y=p["y"]*h; glow=(math.sin(p["p"])+1)/2
            shade="#371018" if glow>.65 else "#1B0B0E"; r=p["r"]
            c.create_oval(x-r,y-r,x+r,y+r,fill=shade,outline="")
        cx,cy=w/2,h/2; base=min(w,h)*.19; pulse=1+math.sin(self.pulse)*(.025+self.activity*.04); r=base*pulse
        for s,col,wd in ((1.95,"#180A0D",1),(1.72,"#321017",1),(1.48,LINE_HI,2),(1.18,"#65131D",1)):
            rr=r*s; c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline=col,width=wd)
        for i in range(44):
            a=math.radians(i*360/44+self.angle*.3); rr=r*1.82; ln=8 if i%4 else 15
            x1=cx+math.cos(a)*(rr-ln); y1=cy+math.sin(a)*(rr-ln); x2=cx+math.cos(a)*rr; y2=cy+math.sin(a)*rr
            c.create_line(x1,y1,x2,y2,fill="#50131B",width=1)
        for off,ext,col,wd in ((0,70,RED,3),(92,48,RED_SOFT,2),(188,76,LINE_HI,2),(294,38,RED,2)):
            rr=r*1.48; c.create_arc(cx-rr,cy-rr,cx+rr,cy+rr,start=(self.angle+off)%360,extent=ext,style="arc",outline=col,width=wd)
        for k in range(12 if not perf else 5):
            a=self.angle*.018+k*math.tau/(12 if not perf else 5); rr=r*(1.25+.38*math.sin(self.pulse*.7+k)); x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr
            c.create_oval(x-2,y-2,x+2,y+2,fill=RED,outline="")
        eye_w=r*1.25; eye_h=r*.34
        pts=[cx-eye_w,cy,cx-eye_w*.38,cy-eye_h,cx,cy-eye_h*.36,cx+eye_w*.38,cy-eye_h,cx+eye_w,cy,cx+eye_w*.38,cy+eye_h,cx,cy+eye_h*.36,cx-eye_w*.38,cy+eye_h]
        c.create_polygon(pts,outline=RED,fill="#100306",width=2)
        iris=r*(.31+self.activity*.06); c.create_oval(cx-iris,cy-iris,cx+iris,cy+iris,fill=RED_DARK,outline=RED,width=3); pupil=iris*.35; c.create_oval(cx-pupil,cy-pupil,cx+pupil,cy+pupil,fill=RED,outline="")
        state="LISTENING" if self.listening else ("COGNITION ACTIVE" if self.processing else "STANDING BY")
        col=GREEN if self.listening else (AMBER if self.processing else RED)
        c.create_text(cx,cy+r*2.12,text="ULTRON // PRIME COGNITIVE REACTOR",fill=MUTED,font=("Consolas",9,"bold")); c.create_text(cx,cy+r*2.32,text=state,fill=col,font=("Consolas",9,"bold"))
        self.angle=(self.angle+(.55 if perf else 1.15)+self.activity*1.5)%360; self.pulse+=.055+self.activity*.04
        self.after(50 if perf else 25,self._animate_core)

    app_cls._top_button=top_button
    app_cls._metric=metric
    app_cls._build_header=build_header
    app_cls._build_body=build_body
    app_cls._build_command_bar=build_command_bar
    app_cls._animate_core=animate_core
    app_cls._ui_v3_installed=True
