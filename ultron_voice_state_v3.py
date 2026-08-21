from __future__ import annotations

import re

AMBER="#FFBE63"; RED="#FF3045"; MUTED="#7D7D88"


def install_voice_state_v3(app_cls) -> None:
    if getattr(app_cls,"_voice_state_v3_installed",False): return
    original=app_cls._assistant
    def assistant(self,text:str,speak:bool):
        result=original(self,text,speak)
        if speak and getattr(self,"voice_enabled",False):
            try:
                words=max(1,len(re.findall(r"\w+",text)))
                duration=min(12000,max(900,int(words/2.7*1000)))
                self.after(40,lambda:self.status_badge.configure(text="  SPEAKING  ",text_color=AMBER))
                self.after(40,lambda:self.mode_label.configure(text="MODE // VOICE OUTPUT",text_color=AMBER))
                def restore():
                    if not getattr(self,"processing",False) and not getattr(self,"listening",False):
                        self.status_badge.configure(text="  CORE ONLINE  ",text_color=RED)
                        self.mode_label.configure(text="MODE // READY",text_color=MUTED)
                self.after(duration,restore)
            except Exception: pass
        return result
    app_cls._assistant=assistant; app_cls._voice_state_v3_installed=True
