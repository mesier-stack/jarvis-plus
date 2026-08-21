from __future__ import annotations
import time
import customtkinter as ctk

VOID="#020203"; PANEL="#08080B"; LINE="#381017"; RED="#FF3045"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"; AMBER="#FFBE63"

def install_performance_dashboard_v6(app_cls):
    if getattr(app_cls,"_perf_dash_v6",False): return
    old=app_cls.__init__
    def init(self,*a,**k): old(self,*a,**k); self.bind("<Control-Shift-P>",lambda _e:self._open_perf_dash_v6())
    def open_perf(self):
        w=ctk.CTkToplevel(self); w.title("ULTRON // Performance"); w.geometry("760x560"); w.configure(fg_color=VOID); w.transient(self)
        ctk.CTkLabel(w,text="PERFORMANCE CORE",font=ctk.CTkFont("Segoe UI",27,"bold"),text_color=WHITE).pack(anchor="w",padx=22,pady=(20,2)); ctk.CTkLabel(w,text="CPU / MEMORY / STORAGE / UI LOAD",font=ctk.CTkFont("Consolas",9,"bold"),text_color=RED).pack(anchor="w",padx=22)
        body=ctk.CTkFrame(w,fg_color=VOID); body.pack(fill="both",expand=True,padx=18,pady=18)
        labels={}
        for key in ("CPU","RAM","STORAGE","PARTICLES","ANIMATION","PROFILE"):
            r=ctk.CTkFrame(body,fg_color=PANEL,border_width=1,border_color=LINE,corner_radius=9); r.pack(fill="x",pady=5); ctk.CTkLabel(r,text=key,font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(side="left",padx=14,pady=13); labels[key]=ctk.CTkLabel(r,text="--",font=ctk.CTkFont("Consolas",10,"bold"),text_color=WHITE); labels[key].pack(side="right",padx=14)
        def tick():
            try:
                import psutil
                cpu=psutil.cpu_percent(); ram=psutil.virtual_memory().percent; disk=psutil.disk_usage('C:\\' if __import__('os').name=='nt' else '/').percent
                labels["CPU"].configure(text=f"{cpu:.0f}%",text_color=GREEN if cpu<70 else AMBER); labels["RAM"].configure(text=f"{ram:.0f}%",text_color=GREEN if ram<80 else AMBER); labels["STORAGE"].configure(text=f"{disk:.0f}%")
            except Exception: pass
            labels["PARTICLES"].configure(text=self.brain.memory.get_setting("ultron_particles","high").upper()); labels["ANIMATION"].configure(text=self.brain.memory.get_setting("ultron_animation","intense").upper()); labels["PROFILE"].configure(text=self.brain.memory.get_setting("ultron_profile","balanced").upper())
            if w.winfo_exists(): w.after(900,tick)
        tick()
    app_cls.__init__=init; app_cls._open_perf_dash_v6=open_perf; app_cls._perf_dash_v6=True