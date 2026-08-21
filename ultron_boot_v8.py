from __future__ import annotations
import customtkinter as ctk
VOID='#020203';RED='#FF3045';WHITE='#F7F7FA';MUTED='#7D7D88'
def install_boot_v8(app_cls):
    if getattr(app_cls,'_boot_v8',False): return
    old=app_cls.__init__
    def init(self,*a,**k):
        old(self,*a,**k)
        if self.brain.memory.get_setting('ultron_boot_sequence','on')=='on': self.after(100,self._boot_v8)
    def boot(self):
        w=ctk.CTkToplevel(self);w.overrideredirect(True);w.geometry('620x320');w.configure(fg_color=VOID);w.attributes('-topmost',True);w.update_idletasks();x=(w.winfo_screenwidth()-620)//2;y=(w.winfo_screenheight()-320)//2;w.geometry(f'620x320+{x}+{y}')
        ctk.CTkLabel(w,text='◉',font=ctk.CTkFont('Segoe UI',64,'bold'),text_color=RED).pack(pady=(48,2));ctk.CTkLabel(w,text='ULTRON',font=ctk.CTkFont('Segoe UI',34,'bold'),text_color=WHITE).pack();state=ctk.CTkLabel(w,text='INITIALIZING PRIME CORE',font=ctk.CTkFont('Consolas',9,'bold'),text_color=MUTED);state.pack(pady=8);bar=ctk.CTkProgressBar(w,width=400,progress_color=RED);bar.pack(pady=14);bar.set(0)
        stages=[('LOADING MEMORY',.2),('LINKING NEMOTRON',.4),('ARMING VISION',.6),('SYNCING MODULES',.8),('CORE ONLINE',1.0)]
        def step(i=0):
            if i>=len(stages): w.after(280,w.destroy);return
            text,val=stages[i];state.configure(text=text);bar.set(val);w.after(170,lambda:step(i+1))
        step()
    app_cls.__init__=init;app_cls._boot_v8=boot;app_cls._boot_v8_installed=True