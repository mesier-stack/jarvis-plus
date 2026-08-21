from __future__ import annotations
import customtkinter as ctk
from ultron_learning_v10 import learning_summary, learned_insights

VOID='#020203';PANEL='#08080B';LINE='#381017';RED='#FF3045';WHITE='#F7F7FA';MUTED='#7D7D88'

def install_learning_ui_v10(app_cls):
    if getattr(app_cls,'_learning_ui_v10',False): return
    old=app_cls.__init__
    def init(self,*a,**k):
        old(self,*a,**k); self.bind('<Control-Shift-L>',lambda _e:self._open_learning_v10())
    def open_learning(self):
        w=ctk.CTkToplevel(self);w.title('ULTRON // Learning Core');w.geometry('820x640');w.configure(fg_color=VOID);w.transient(self)
        ctk.CTkLabel(w,text='LEARNING CORE',font=ctk.CTkFont('Segoe UI',28,'bold'),text_color=WHITE).pack(anchor='w',padx=22,pady=(20,2))
        ctk.CTkLabel(w,text='SELF LEARNING / ERROR LEARNING',font=ctk.CTkFont('Consolas',9,'bold'),text_color=RED).pack(anchor='w',padx=22)
        box=ctk.CTkTextbox(w,fg_color=PANEL,border_width=1,border_color=LINE,text_color=WHITE,font=ctk.CTkFont('Consolas',10));box.pack(fill='both',expand=True,padx=22,pady=18)
        box.insert('end',learning_summary()+'\n\nTOP LEARNED PATTERNS\n')
        for line in learned_insights(10): box.insert('end',line+'\n')
        box.configure(state='disabled')
        ctk.CTkLabel(w,text='Learning is local. ULTRON does not rewrite its own code automatically.',font=ctk.CTkFont('Consolas',8),text_color=MUTED).pack(anchor='w',padx=22,pady=(0,18))
    app_cls.__init__=init;app_cls._open_learning_v10=open_learning;app_cls._learning_ui_v10=True