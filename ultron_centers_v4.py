from __future__ import annotations

import os
from pathlib import Path
import customtkinter as ctk
from PIL import Image

VOID="#020203"; PANEL="#08080B"; PANEL2="#0D0D12"; LINE="#381017"; RED="#FF3045"; RED_DARK="#410811"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"; AMBER="#FFBE63"

def _window(app,title,size="760x620"):
    w=ctk.CTkToplevel(app); w.title(title); w.geometry(size); w.configure(fg_color=VOID); w.transient(app); return w

def install_centers_v4(app_cls):
    if getattr(app_cls,"_centers_v4",False): return
    old=app_cls.__init__
    def init(self,*a,**k):
        old(self,*a,**k)
        self.open_memory_center=lambda:self._memory_center_v4()
        self.open_vision_center=lambda:self._vision_center_v4()
        self.open_voice_center=lambda:self._voice_center_v4()
    def memory_center(self):
        w=_window(self,"ULTRON // Memory Center"); ctk.CTkLabel(w,text="MEMORY CENTER",font=ctk.CTkFont("Segoe UI",26,"bold"),text_color=WHITE).pack(anchor="w",padx=22,pady=(20,2)); ctk.CTkLabel(w,text="Persistent local memories // searchable, addable and removable",font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(anchor="w",padx=22)
        search=ctk.CTkEntry(w,placeholder_text="Search memory...",height=38,fg_color=PANEL,border_width=1,border_color=LINE,text_color=WHITE); search.pack(fill="x",padx=22,pady=14)
        box=ctk.CTkScrollableFrame(w,fg_color=PANEL,corner_radius=10,border_width=1,border_color=LINE); box.pack(fill="both",expand=True,padx=22,pady=(0,12))
        def render(*_):
            for child in box.winfo_children(): child.destroy()
            needle=search.get().lower().strip(); items=self.brain.memory.list_memories(200)
            for item in items:
                if needle and needle not in item.lower(): continue
                row=ctk.CTkFrame(box,fg_color=PANEL2,corner_radius=8); row.pack(fill="x",padx=8,pady=4); ctk.CTkLabel(row,text=item,wraplength=560,justify="left",text_color=WHITE,font=ctk.CTkFont("Consolas",9)).pack(side="left",fill="x",expand=True,padx=10,pady=10)
                ctk.CTkButton(row,text="FORGET",width=76,fg_color="transparent",hover_color=RED_DARK,border_width=1,border_color=RED,command=lambda x=item:(self.brain.memory.forget_memory(x),render())).pack(side="right",padx=8)
        search.bind("<KeyRelease>",render); render()
        add=ctk.CTkEntry(w,placeholder_text="New memory...",height=38,fg_color=PANEL,border_width=1,border_color=LINE,text_color=WHITE); add.pack(fill="x",padx=22,pady=(0,8))
        def remember():
            t=add.get().strip()
            if t: self.brain.memory.remember(t); add.delete(0,"end"); render()
        ctk.CTkButton(w,text="REMEMBER",command=remember,fg_color=RED_DARK,border_width=1,border_color=RED).pack(anchor="e",padx=22,pady=(0,18))
    def vision_center(self):
        w=_window(self,"ULTRON // Vision Center","820x680"); ctk.CTkLabel(w,text="VISION CENTER",font=ctk.CTkFont("Segoe UI",26,"bold"),text_color=WHITE).pack(anchor="w",padx=22,pady=(20,2)); ctk.CTkLabel(w,text="On-demand screen perception // no camera required",font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(anchor="w",padx=22)
        preview=ctk.CTkLabel(w,text="NO CAPTURE PREVIEW YET",height=420,fg_color=PANEL,corner_radius=10,text_color=MUTED); preview.pack(fill="both",expand=True,padx=22,pady=18)
        info=ctk.CTkLabel(w,text="",font=ctk.CTkFont("Consolas",8),text_color=MUTED); info.pack(anchor="w",padx=22)
        def refresh():
            root=Path.home()/"Pictures"/"ULTRON"; files=sorted(root.glob("*.png"),key=lambda p:p.stat().st_mtime,reverse=True) if root.exists() else []
            if not files: info.configure(text="VISION HISTORY // 0 CAPTURES"); return
            p=files[0]
            try:
                im=Image.open(p); im.thumbnail((730,390)); photo=ctk.CTkImage(light_image=im,dark_image=im,size=im.size); preview.configure(image=photo,text=""); preview.image=photo
            except Exception: preview.configure(text=str(p.name),image=None)
            info.configure(text=f"LATEST // {p.name}   //   HISTORY {len(files)}")
        def analyze(): self._quick("look at my screen"); self.after(1800,refresh)
        row=ctk.CTkFrame(w,fg_color="transparent"); row.pack(fill="x",padx=22,pady=(8,18)); ctk.CTkButton(row,text="ANALYZE SCREEN",command=analyze,fg_color=RED_DARK,border_width=1,border_color=RED).pack(side="left"); ctk.CTkButton(row,text="REFRESH PREVIEW",command=refresh,fg_color=PANEL2,border_width=1,border_color=LINE).pack(side="left",padx=8); refresh()
    def voice_center(self):
        w=_window(self,"ULTRON // Voice Center"); ctk.CTkLabel(w,text="VOICE CENTER",font=ctk.CTkFont("Segoe UI",26,"bold"),text_color=WHITE).pack(anchor="w",padx=22,pady=(20,2)); ctk.CTkLabel(w,text="Speech input, synthesis and bilingual behavior",font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(anchor="w",padx=22)
        panel=ctk.CTkFrame(w,fg_color=PANEL,corner_radius=10,border_width=1,border_color=LINE); panel.pack(fill="both",expand=True,padx=22,pady=18)
        engine="ELEVENLABS / CLOUD" if self.voice.cloud_available else ("WINDOWS LOCAL" if self.voice.available else "TEXT ONLY")
        for label,value in (("ENGINE",engine),("LANGUAGE",self.brain.memory.get_setting("voice_language","auto").upper()),("SPEED",self.brain.memory.get_setting("voice_speed","fast").upper()),("PROFILE",self.brain.memory.get_setting("voice_profile","cinematic").upper())):
            r=ctk.CTkFrame(panel,fg_color=PANEL2,corner_radius=7); r.pack(fill="x",padx=12,pady=5); ctk.CTkLabel(r,text=label,text_color=MUTED,font=ctk.CTkFont("Consolas",9)).pack(side="left",padx=10,pady=10); ctk.CTkLabel(r,text=value,text_color=RED,font=ctk.CTkFont("Consolas",9,"bold")).pack(side="right",padx=10)
        def set_lang(v): self.brain.memory.set_setting("voice_language",v); self.voice.set_language(v)
        def set_speed(v): self.brain.memory.set_setting("voice_speed",v); self.voice.set_speed(v)
        ctk.CTkLabel(panel,text="LANGUAGE",text_color=MUTED,font=ctk.CTkFont("Consolas",8)).pack(anchor="w",padx=12,pady=(16,3)); ctk.CTkSegmentedButton(panel,values=["auto","es","en"],command=set_lang).pack(fill="x",padx=12)
        ctk.CTkLabel(panel,text="SPEED",text_color=MUTED,font=ctk.CTkFont("Consolas",8)).pack(anchor="w",padx=12,pady=(16,3)); ctk.CTkSegmentedButton(panel,values=["slow","normal","fast"],command=set_speed).pack(fill="x",padx=12)
        row=ctk.CTkFrame(panel,fg_color="transparent"); row.pack(fill="x",padx=12,pady=20); ctk.CTkButton(row,text="MIC TEST",command=self._start_listen_once,fg_color=PANEL2,border_width=1,border_color=LINE).pack(side="left"); ctk.CTkButton(row,text="VOICE TEST",command=lambda:self._assistant("Voice system online.",speak=True),fg_color=RED_DARK,border_width=1,border_color=RED).pack(side="left",padx=8)
    app_cls.__init__=init; app_cls._memory_center_v4=memory_center; app_cls._vision_center_v4=vision_center; app_cls._voice_center_v4=voice_center; app_cls._centers_v4=True