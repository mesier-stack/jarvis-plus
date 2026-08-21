from __future__ import annotations
import customtkinter as ctk
VOID='#020203';PANEL='#08080B';LINE='#381017';RED='#FF3045';WHITE='#F7F7FA';MUTED='#7D7D88';GREEN='#59F6A3';AMBER='#FFBE63'
MODULES=[('NVIDIA','AI cognition'),('VISION','Screen understanding'),('VOICE','Speech I/O'),('MEMORY','Local memory'),('UPDATER','Update/rollback'),('SKILLS','Plugin manifests'),('BRAIN','Neural visualization'),('TRAY','System tray'),('WATCH','Watch mode'),('OVERLAY','Mini overlay')]
def install_module_manager_v9(app_cls):
    if getattr(app_cls,'_module_manager_v9',False): return
    old=app_cls.__init__
    def init(self,*a,**k): old(self,*a,**k);self.bind('<Control-m>',lambda _e:self._module_manager_v9())
    def show(self):
        w=ctk.CTkToplevel(self);w.title('ULTRON // Module Manager');w.geometry('760x620');w.configure(fg_color=VOID);w.transient(self)
        ctk.CTkLabel(w,text='MODULE MANAGER',font=ctk.CTkFont('Segoe UI',27,'bold'),text_color=WHITE).pack(anchor='w',padx=22,pady=(20,2));ctk.CTkLabel(w,text='RUNTIME MODULE HEALTH',font=ctk.CTkFont('Consolas',9,'bold'),text_color=RED).pack(anchor='w',padx=22)
        body=ctk.CTkScrollableFrame(w,fg_color=VOID);body.pack(fill='both',expand=True,padx=16,pady=14)
        safe=self.brain.memory.get_setting('ultron_safe_mode','off')=='on'
        for name,desc in MODULES:
            active=True
            if name=='NVIDIA': active=getattr(self.brain.ai,'provider','local')=='nvidia'
            if name=='VOICE': active=bool(getattr(self.voice,'available',False))
            if name in {'WATCH','OVERLAY','TRAY'} and safe: active=False
            r=ctk.CTkFrame(body,fg_color=PANEL,border_width=1,border_color=LINE);r.pack(fill='x',pady=4)
            ctk.CTkLabel(r,text=name,width=120,anchor='w',font=ctk.CTkFont('Consolas',9,'bold'),text_color=RED).pack(side='left',padx=12,pady=11);ctk.CTkLabel(r,text=desc,text_color=WHITE).pack(side='left');ctk.CTkLabel(r,text='ONLINE' if active else ('SAFE-OFF' if safe else 'STANDBY'),font=ctk.CTkFont('Consolas',8,'bold'),text_color=GREEN if active else AMBER).pack(side='right',padx=12)
    app_cls.__init__=init;app_cls._module_manager_v9=show;app_cls._module_manager_v9_installed=True