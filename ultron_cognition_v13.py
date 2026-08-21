from __future__ import annotations
import json, os, sqlite3, time
from pathlib import Path
from ultron_core import AssistantReply, UltronBrain

ROOT=Path(os.getenv('APPDATA',Path.home()))/'ULTRON'
DB=ROOT/'cognition.db'

def _db():
    ROOT.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(DB)
    con.executescript('''
    CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY,title TEXT,status TEXT,created REAL,updated REAL);
    CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY,goal_id INTEGER,title TEXT,status TEXT,created REAL,updated REAL);
    CREATE TABLE IF NOT EXISTS nodes(id INTEGER PRIMARY KEY,label TEXT UNIQUE,kind TEXT,weight REAL DEFAULT 1,updated REAL);
    CREATE TABLE IF NOT EXISTS edges(a TEXT,b TEXT,relation TEXT,weight REAL DEFAULT 1,updated REAL,UNIQUE(a,b,relation));
    CREATE TABLE IF NOT EXISTS reflections(id INTEGER PRIMARY KEY,summary TEXT,created REAL);
    ''')
    return con

def _goal_add(title):
    with _db() as d:
        cur=d.execute('INSERT INTO goals(title,status,created,updated) VALUES(?,?,?,?)',(title,'active',time.time(),time.time())); return cur.lastrowid

def _task_add(goal_id,title):
    with _db() as d: d.execute('INSERT INTO tasks(goal_id,title,status,created,updated) VALUES(?,?,?,?,?)',(goal_id,title,'todo',time.time(),time.time()))

def _goals():
    with _db() as d: return d.execute('SELECT id,title,status FROM goals ORDER BY updated DESC LIMIT 20').fetchall()

def _tasks(goal_id):
    with _db() as d: return d.execute('SELECT id,title,status FROM tasks WHERE goal_id=? ORDER BY id',(goal_id,)).fetchall()

def _graph_link(a,b,relation='related'):
    now=time.time()
    with _db() as d:
        for label,kind in ((a,'concept'),(b,'concept')):
            d.execute('INSERT INTO nodes(label,kind,updated) VALUES(?,?,?) ON CONFLICT(label) DO UPDATE SET weight=MIN(weight+0.1,5),updated=excluded.updated',(label,kind,now))
        d.execute('INSERT INTO edges(a,b,relation,updated) VALUES(?,?,?,?) ON CONFLICT(a,b,relation) DO UPDATE SET weight=MIN(weight+0.2,5),updated=excluded.updated',(a,b,relation,now))

def _reflect(brain):
    try:
        learned,uses,failures=brain.memory.learning_stats()
    except Exception: learned=uses=failures=0
    goals=_goals(); active=sum(1 for _i,_t,s in goals if s=='active')
    summary=f'Active goals: {active}. Learned commands: {learned}. Learned uses: {uses}. Failures observed: {failures}.'
    with _db() as d: d.execute('INSERT INTO reflections(summary,created) VALUES(?,?)',(summary,time.time()))
    brain.memory.set_setting('ultron_last_reflection',summary)
    return summary

def install_cognition_v13():
    if getattr(UltronBrain,'_cognition_v13',False): return
    old=UltronBrain.handle
    def handle(self,raw):
        text=raw.strip(); low=text.lower().strip(' .!?¿¡')
        for prefix in ('new goal ','goal ','nuevo objetivo '):
            if low.startswith(prefix):
                title=text[len(prefix):].strip(); gid=_goal_add(title); _graph_link('ULTRON',title,'goal')
                return AssistantReply(f'GOAL #{gid} // ACTIVE\n{title}\nSay: add task {gid} <task>','status')
        if low.startswith('add task '):
            parts=text.split(maxsplit=3)
            if len(parts)>=4 and parts[2].isdigit():
                gid=int(parts[2]); title=parts[3]; _task_add(gid,title); _graph_link(f'goal:{gid}',title,'task')
                return AssistantReply(f'TASK // ADDED TO GOAL {gid}\n{title}','status')
        if low in {'goals','goal status','my goals','objetivos'}:
            rows=_goals()
            return AssistantReply('GOAL ENGINE // '+('EMPTY' if not rows else '\n'+'\n'.join(f'#{i} [{s.upper()}] {t}' for i,t,s in rows)),'status')
        if low.startswith('tasks '):
            try: gid=int(low.split()[1]); rows=_tasks(gid)
            except Exception: rows=[]
            return AssistantReply('TASK MEMORY // '+('EMPTY' if not rows else '\n'+'\n'.join(f'#{i} [{s.upper()}] {t}' for i,t,s in rows)),'status')
        if low.startswith('link concept '):
            body=text[len('link concept '):]
            if ' -> ' in body:
                a,b=body.split(' -> ',1); _graph_link(a.strip(),b.strip()); return AssistantReply(f'KNOWLEDGE GRAPH // LINKED\n{a.strip()} → {b.strip()}','status')
        if low in {'reflect','reflection','session reflection','reflexiona'}:
            return AssistantReply('REFLECTION LOOP // COMPLETE\n'+_reflect(self),'status')
        if low in {'last reflection','reflection status'}:
            return AssistantReply('LAST REFLECTION // '+self.memory.get_setting('ultron_last_reflection','none'),'status')
        return old(self,raw)
    UltronBrain.handle=handle; UltronBrain._cognition_v13=True
