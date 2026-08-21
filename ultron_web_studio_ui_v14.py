from __future__ import annotations
import customtkinter as ctk
VOID='#020203';PANEL='#08080B';LINE='#381017';RED='#FF3045';WHITE='#F7F7FA';MUTED='#7D7D88'
def install_web_studio_ui_v14(app_cls):
    if getattr(app_cls,'_web_studio_ui_v14',False): return
    old=app_cls.__init__
    def init(self,*a,**k): old(self,*a,**k); self.bind('<Control-Shift-W>',lambda _e:self._open_web_studio_v14())
    def open_studio(self):
        w=ctk.CTkToplevel(self);w.title('ULTRON // Web Studio');w.geometry('980x690');w.configure(fg_color=VOID);w.transient(self)
        ctk.CTkLabel(w,text='WEB STUDIO',font=ctk.CTkFont('Segoe UI',30,'bold'),text_color=WHITE).pack(anchor='w',padx=24,pady=(22,2));ctk.CTkLabel(w,text='ART DIRECTION / ARCHITECTURE / PREMIUM QA',font=ctk.CTkFont('Consolas',9,'bold'),text_color=RED).pack(anchor='w',padx=24)
        body=ctk.CTkFrame(w,fg_color=PANEL,border_width=1,border_color=LINE);body.pack(fill='both',expand=True,padx=24,pady=18)
        brief=ctk.CTkTextbox(body,height=250,fg_color=VOID,border_width=1,border_color=LINE,text_color=WHITE);brief.pack(fill='x',padx=16,pady=(16,10));brief.insert('1.0','Describe the brand, audience, goals, content, desired feeling, references, must-have features, and anything to avoid.')
        row=ctk.CTkFrame(body,fg_color='transparent');row.pack(fill='x',padx=16,pady=8)
        def send(cmd): self._quick(cmd)
        def create(): send('new website '+brief.get('1.0','end').strip())
        for label,fn in [('CREATE PROJECT',create),('DESIGN DOSSIER',lambda:send('design website')),('RUN ARCHITECT',lambda:send('run website architect')),('STATUS',lambda:send('web studio status'))]: ctk.CTkButton(row,text=label,command=fn,fg_color='#410811',border_width=1,border_color=RED).pack(side='left',padx=4)
        ctk.CTkLabel(body,text='QUALITY GATE',font=ctk.CTkFont('Consolas',10,'bold'),text_color=RED).pack(anchor='w',padx=16,pady=(18,4))
        ctk.CTkLabel(body,text='Anti-template rules: no generic hero/card stacks, deliberate typography, responsive composition, accessibility, restrained motion, performance budget, brand-specific visual thesis.',wraplength=880,justify='left',text_color=MUTED).pack(anchor='w',padx=16)
    app_cls.__init__=init;app_cls._open_web_studio_v14=open_studio;app_cls._web_studio_ui_v14=True