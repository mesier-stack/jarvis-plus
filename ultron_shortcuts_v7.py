from __future__ import annotations
import customtkinter as ctk
VOID='#020203';PANEL='#08080B';LINE='#381017';RED='#FF3045';WHITE='#F7F7FA';MUTED='#7D7D88'
SHORTCUTS=[('CTRL + K','Command Palette'),('CTRL + ALT + U','Summon ULTRON'),('CTRL + H','Home Dashboard'),('CTRL + ,','Control Center'),('CTRL + D','Diagnostics'),('CTRL + N','Notifications'),('CTRL + Q','Quick Actions'),('CTRL + P','Performance'),('CTRL + SHIFT + A','Session Analytics'),('CTRL + SHIFT + M','Memory Center'),('CTRL + SHIFT + V','Vision Center'),('CTRL + SHIFT + S','Voice Center'),('F1','Shortcut Map')]
def install_shortcuts_v7(app_cls):
    if getattr(app_cls,'_shortcuts_v7',False): return
    old=app_cls.__init__
    def init(self,*a,**k): old(self,*a,**k); self.bind('<F1>',lambda _e:self._shortcut_map_v7())
    def show(self):
        w=ctk.CTkToplevel(self);w.title('ULTRON // Shortcut Matrix');w.geometry('650x600');w.configure(fg_color=VOID);w.transient(self)
        ctk.CTkLabel(w,text='SHORTCUT MATRIX',font=ctk.CTkFont('Segoe UI',26,'bold'),text_color=WHITE).pack(anchor='w',padx=22,pady=(20,4));body=ctk.CTkScrollableFrame(w,fg_color=VOID);body.pack(fill='both',expand=True,padx=16,pady=10)
        for key,name in SHORTCUTS:
            r=ctk.CTkFrame(body,fg_color=PANEL,border_width=1,border_color=LINE);r.pack(fill='x',pady=4);ctk.CTkLabel(r,text=key,width=170,anchor='w',font=ctk.CTkFont('Consolas',10,'bold'),text_color=RED).pack(side='left',padx=12,pady=11);ctk.CTkLabel(r,text=name,font=ctk.CTkFont('Segoe UI',11),text_color=WHITE).pack(side='left')
    app_cls.__init__=init;app_cls._shortcut_map_v7=show;app_cls._shortcuts_v7=True