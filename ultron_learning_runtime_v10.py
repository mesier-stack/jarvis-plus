from __future__ import annotations
import time
from ultron_learning_v10 import record_command, record_error


def install_learning_runtime_v10(app_cls):
    if getattr(app_cls,'_learning_runtime_v10',False): return
    old_process=app_cls._process
    def process(self,text):
        started=time.perf_counter()
        try:
            result=old_process(self,text)
            record_command(text,True,(time.perf_counter()-started)*1000)
            return result
        except Exception as exc:
            record_command(text,False,(time.perf_counter()-started)*1000)
            record_error(exc,context=f'command:{text[:120]}',recovered=False)
            raise
    app_cls._process=process
    app_cls._learning_runtime_v10=True
