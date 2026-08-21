from __future__ import annotations

import ctypes
import os
import threading
import time
import urllib.request
from collections import deque
from pathlib import Path

import customtkinter as ctk

RED="#FF3045"; RED_DARK="#410811"; WHITE="#F7F7FA"; MUTED="#7D7D88"; GREEN="#59F6A3"; AMBER="#FFBE63"; PANEL="#08080B"; PANEL2="#0D0D12"; LINE="#381017"; LINE_HI="#8F1C2B"; VOID="#020203"
_HISTORY=deque(maxlen=120)
_SAFE_UNDO={"focus mode":"focus mode","performance mode":"performance mode"}


def _startup_file() -> Path:
    appdata=Path(os.getenv("APPDATA", Path.home()))
    return appdata/"Microsoft"/"Windows"/"Start Menu"/"Programs"/"Startup"/"ULTRON.cmd"

def _set_startup(enabled: bool, install_dir: Path) -> bool:
    p=_startup_file(); p.parent.mkdir(parents=True,exist_ok=True)
    if enabled:
        p.write_text(f'@echo off\ncd /d "{install_dir}"\nstart "" "{install_dir / "run_ultron.bat"}"\n',encoding="utf-8")
        return True
    p.unlink(missing_ok=True); return False

def _latest_sha() -> str:
    req=urllib.request.Request("https://api.github.com/repos/mesier-stack/jarvis-plus/commits/main",headers={"User-Agent":"ULTRON-Update-Center"})
    with urllib.request.urlopen(req,timeout=8) as r:
        import json
        return str(json.loads(r.read().decode("utf-8")).get("sha", ""))


def install_ux_v3(app_cls) -> None:
    if getattr(app_cls,"_ux_v3_installed",False): return
    original_init=app_cls.__init__; original_dispatch=app_cls._dispatch; original_assistant=app_cls._assistant; original_close=app_cls._close

    def init(self,*a,**kw):
        original_init(self,*a,**kw)
        self._tray_icon=None; self._global_hotkey_thread=None
        self._install_dir=Path(__file__).resolve().parent
        self._add_v3_header_buttons()
        self._start_global_hotkey()
        self._start_tray()

    def dispatch(self,text:str):
        _HISTORY.appendleft((time.strftime("%H:%M:%S"),"DIRECTIVE",text))
        return original_dispatch(self,text)

    def assistant(self,text:str,speak:bool):
        clean=text.replace("**","").replace("### ","").replace("## ","")
        _HISTORY.appendleft((time.strftime("%H:%M:%S"),"ULTRON",clean[:500]))
        return original_assistant(self,clean,speak)

    def add_buttons(self):
        try:
            parent=self.wake_btn.master
            self._top_button(parent,"AI TEST",lambda:self._quick("test nvidia")).pack(side="left",padx=3)
            self._top_button(parent,"UPDATE",self._open_update_center).pack(side="left",padx=3)
            self._top_button(parent,"HISTORY",self._open_history_v3).pack(side="left",padx=3)
        except Exception: pass

    def open_update(self):
        win=ctk.CTkToplevel(self); win.title("ULTRON // Update Center"); win.geometry("650x430"); win.configure(fg_color=VOID); win.transient(self)
        ctk.CTkLabel(win,text="UPDATE CENTER",font=ctk.CTkFont("Segoe UI",25,"bold"),text_color=WHITE).pack(anchor="w",padx=24,pady=(22,2))
        ctk.CTkLabel(win,text="Source refresh, dependency sync and automatic restart",font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(anchor="w",padx=24)
        box=ctk.CTkTextbox(win,height=210,fg_color=PANEL,border_width=1,border_color=LINE,text_color=WHITE,font=ctk.CTkFont("Consolas",10)); box.pack(fill="x",padx=24,pady=20)
        box.insert("end","STATUS // READY\n\nPress CHECK to compare with the latest repository revision.\nAPI keys and Windows environment variables are never replaced.\n")
        bar=ctk.CTkProgressBar(win,height=8,fg_color=LINE,progress_color=RED); bar.pack(fill="x",padx=24); bar.set(0)
        row=ctk.CTkFrame(win,fg_color="transparent"); row.pack(fill="x",padx=24,pady=18)
        def check():
            box.configure(state="normal"); box.insert("end","\nCHECKING // GitHub main...\n"); bar.set(.35)
            def worker():
                try:
                    sha=_latest_sha(); self.after(0,lambda:done(sha,None))
                except Exception as exc: self.after(0,lambda:done("",exc))
            threading.Thread(target=worker,daemon=True).start()
        def done(sha,err):
            box.configure(state="normal")
            if err: box.insert("end",f"FAILED // {err}\n"); bar.set(0)
            else: box.insert("end",f"LATEST REVISION // {sha[:12]}\nREADY TO INSTALL.\n"); bar.set(.7)
            box.see("end")
        def install():
            bar.set(1); box.configure(state="normal"); box.insert("end","\nINSTALL REQUESTED // preparing safe updater...\n"); box.see("end"); self._quick("update ultron")
        ctk.CTkButton(row,text="CHECK",command=check,width=120,fg_color=PANEL2,hover_color=RED_DARK,border_width=1,border_color=LINE_HI).pack(side="left",padx=(0,8))
        ctk.CTkButton(row,text="INSTALL UPDATE",command=install,width=150,fg_color=RED_DARK,hover_color="#7A1421",border_width=1,border_color=RED).pack(side="left")
        ctk.CTkButton(row,text="CLOSE",command=win.destroy,width=90,fg_color="transparent",border_width=1,border_color=LINE).pack(side="right")

    def open_history(self):
        win=ctk.CTkToplevel(self); win.title("ULTRON // Action History"); win.geometry("760x560"); win.configure(fg_color=VOID); win.transient(self)
        ctk.CTkLabel(win,text="ACTION HISTORY",font=ctk.CTkFont("Segoe UI",24,"bold"),text_color=WHITE).pack(anchor="w",padx=22,pady=(20,2))
        ctk.CTkLabel(win,text="Undo is only offered for explicitly reversible local modes.",font=ctk.CTkFont("Consolas",9),text_color=MUTED).pack(anchor="w",padx=22)
        t=ctk.CTkTextbox(win,fg_color=PANEL,border_width=1,border_color=LINE,text_color=WHITE,font=ctk.CTkFont("Consolas",10)); t.pack(fill="both",expand=True,padx=22,pady=18)
        for stamp,kind,text in list(_HISTORY)[:70]: t.insert("end",f"[{stamp}] {kind}\n{text}\n\n")
        row=ctk.CTkFrame(win,fg_color="transparent"); row.pack(fill="x",padx=22,pady=(0,18))
        def undo():
            for _stamp,kind,text in _HISTORY:
                if kind=="DIRECTIVE" and text.lower().strip() in _SAFE_UNDO:
                    inverse=_SAFE_UNDO[text.lower().strip()]; self._quick(inverse); t.insert("end",f"UNDO // {text}\n"); t.see("end"); return
            t.insert("end","UNDO // no safe reversible action found\n"); t.see("end")
        ctk.CTkButton(row,text="UNDO SAFE",command=undo,width=120,fg_color=RED_DARK,hover_color="#7A1421",border_width=1,border_color=RED).pack(side="left")
        ctk.CTkButton(row,text="CLOSE",command=win.destroy,width=90,fg_color="transparent",border_width=1,border_color=LINE).pack(side="right")

    def start_hotkey(self):
        if os.name!="nt" or self._global_hotkey_thread: return
        def loop():
            user32=ctypes.windll.user32; MOD_CONTROL=0x0002; MOD_ALT=0x0001; WM_HOTKEY=0x0312; hotkey_id=0xA11
            if not user32.RegisterHotKey(None,hotkey_id,MOD_CONTROL|MOD_ALT,ord('U')): return
            msg=ctypes.wintypes.MSG()
            while True:
                r=user32.GetMessageW(ctypes.byref(msg),None,0,0)
                if r<=0: break
                if msg.message==WM_HOTKEY: self.after(0,self._show_from_tray)
            user32.UnregisterHotKey(None,hotkey_id)
        import ctypes.wintypes
        self._global_hotkey_thread=threading.Thread(target=loop,daemon=True); self._global_hotkey_thread.start()

    def show_from_tray(self):
        try: self.deiconify(); self.lift(); self.focus_force()
        except Exception: pass

    def start_tray(self):
        try:
            import pystray
            from PIL import Image,ImageDraw
            img=Image.new("RGB",(64,64),(3,3,4)); d=ImageDraw.Draw(img); d.ellipse((10,10,54,54),outline=(255,48,69),width=5); d.ellipse((25,25,39,39),fill=(255,48,69))
            def show(_i,_item): self.after(0,self._show_from_tray)
            def startup(_i,_item):
                enabled=not _startup_file().exists(); _set_startup(enabled,self._install_dir); self.after(0,lambda:self._system(f"STARTUP // {'ENABLED' if enabled else 'DISABLED'}"))
            def quit_app(_i,_item): self.after(0,self._close)
            icon=pystray.Icon("ULTRON",img,"ULTRON",menu=pystray.Menu(pystray.MenuItem("Show ULTRON",show),pystray.MenuItem("Toggle startup",startup),pystray.MenuItem("Exit",quit_app)))
            self._tray_icon=icon; threading.Thread(target=icon.run,daemon=True).start()
        except Exception: pass

    def close(self):
        try:
            if self._tray_icon: self._tray_icon.stop()
        except Exception: pass
        return original_close(self)

    app_cls.__init__=init; app_cls._dispatch=dispatch; app_cls._assistant=assistant
    app_cls._add_v3_header_buttons=add_buttons; app_cls._open_update_center=open_update; app_cls._open_history_v3=open_history; app_cls._start_global_hotkey=start_hotkey; app_cls._show_from_tray=show_from_tray; app_cls._start_tray=start_tray; app_cls._close=close
    app_cls._ux_v3_installed=True
