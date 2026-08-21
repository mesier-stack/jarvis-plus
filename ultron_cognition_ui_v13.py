from __future__ import annotations
import sqlite3, os
from pathlib import Path
import customtkinter as ctk
ROOT=Path(os.getenv('APPDATA',Path.home()))/'ULTRON'; DB=ROOT/'cognition.db'
VOID='#020203';PANEL='#08080B';LINE='#381017';RED='#FF3045';WHITE='#F7F7FA';MUTED='#7D7D88';GREEN='#59F6A3'

def install_cognition_ui_v13(app_cls):
    if getattr(app_cls,'_cognition_ui_v13',False): return
    old=app_cls.__init__
    def init(self,*a,**k): old(self,*a,**k); self.bind('<Control-Shift-G>',lambda _e:self._open_cognition_v13())
    def open_ui(self):
        w=ctk.CTkToplevel(self); w.title('ULTRON // Cognition Center'); w.geometry('980x700'); w.configure(fg_color=VOID); w.transient(self)
        ctk.CTkLabel(w,text='COGNITION CENTER',font=ctk.CTkFont('Segoe UI',28,'bold'),text_color=WHITE).pack(anchor='w',padx=22,pady=(20,2))
        ctk.CTkLabel(w,text='GOALS / TASK MEMORY / KNOWLEDGE GRAPH / REFLECTION',font=ctk.CTkFont('Consolas',9,'bold'),text_color=RED).pack(anchor='w',padx=22)
        tabs=ctk.CTkTabview(w,fg_color=PANEL,border_width=1,border_color=LINE); tabs.pack(fill='both',expand=True,padx=22,pady=18)
        for n in ('GOALS','GRAPH','REFLECTION'): tabs.add(n)
        try:
            con=sqlite3.connect(DB)
            goals=con.execute('SELECT id,title,status FROM goals ORDER BY updated DESC LIMIT 50').fetchall()
            edges=con.execute('SELECT a,b,relation,weight FROM edges ORDER BY updated DESC LIMIT 80').fetchall()
            refs=con.execute('SELECT summary,created FROM reflections ORDER BY id DESC LIMIT 30').fetchall(); con.close()
        except Exception: goals=[]; edges=[]; refs=[]
        g=ctk.CTkTextbox(tabs.tab('GOALS'),fg_color=VOID,text_color=WHITE); g.pack(fill='both',expand=True,padx=8,pady=8)
        for i,t,s in goals: g.insert('end',f'#{i} [{s.upper()}] {t}\n')
        gr=ctk.CTkTextbox(tabs.tab('GRAPH'),fg_color=VOID,text_color=WHITE); gr.pack(fill='both',expand=True,padx=8,pady=8)
        for a,b,r,wt in edges: gr.insert('end',f'{a} --{r}/{wt:.1f}--> {b}\n')
        rf=ctk.CTkTextbox(tabs.tab('REFLECTION'),fg_color=VOID,text_color=WHITE); rf.pack(fill='both',expand=True,padx=8,pady=8)
        for s,_ts in refs: rf.insert('end',s+'\n\n')
        ctk.CTkButton(w,text='RUN REFLECTION',command=lambda:self._quick('reflect'),fg_color='#410811',border_width=1,border_color=RED).pack(anchor='w',padx=22,pady=(0,18))
    app_cls.__init__=init; app_cls._open_cognition_v13=open_ui; app_cls._cognition_ui_v13=True
