from __future__ import annotations
import json, os, re, sqlite3, time
from pathlib import Path
from ultron_core import AssistantReply, UltronBrain

ROOT=Path(os.getenv('APPDATA',Path.home()))/'ULTRON'/'web_studio'
DB=ROOT/'studio.db'

def _db():
    ROOT.mkdir(parents=True,exist_ok=True); db=sqlite3.connect(DB)
    db.executescript('''CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY,name TEXT,brief TEXT,status TEXT,created REAL,updated REAL);CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY,project_id INTEGER,score REAL,notes TEXT,created REAL);''');return db

DESIGN_RULES='''You are ULTRON Web Studio, a senior digital art director + frontend engineer. Produce bespoke, premium work. Never default to generic hero/three-card/testimonial/footer layouts. Establish a clear visual thesis first. Use deliberate typography, spacing rhythm, asymmetry where appropriate, editorial composition, strong hierarchy, restrained motion, and responsive behavior. Avoid random gradients, gratuitous glass, excessive rounded cards, stock SaaS copy, repeated icon-card grids, generic lorem ipsum, and template-like section order. Every section must earn its place. Design mobile intentionally, not as a collapsed desktop. Prefer semantic HTML, accessible contrast, keyboard navigation, reduced-motion support, performance budgets, and maintainable component boundaries. Use advanced effects only when they support the brand. Before finalizing, critique the result for originality, hierarchy, spacing, responsiveness, accessibility, performance, and brand coherence, then revise weak areas.'''

def _quality_score(text:str)->tuple[int,list[str]]:
    low=text.lower(); score=100; notes=[]
    bad=[('three cards',12),('3 cards',12),('lorem ipsum',18),('generic',6),('gradient',3),('glassmorphism',4)]
    for term,p in bad:
        if term in low: score-=p;notes.append(f'Penalty: {term}')
    if len(text)<350: score-=18;notes.append('Brief/design direction too shallow')
    if not any(k in low for k in ('typography','type scale','font')): score-=8;notes.append('Typography direction missing')
    if not any(k in low for k in ('mobile','responsive','breakpoint')): score-=10;notes.append('Responsive strategy missing')
    if not any(k in low for k in ('accessibility','contrast','keyboard')): score-=7;notes.append('Accessibility strategy missing')
    return max(0,score),notes

def _studio_prompt(brief:str)->str:
    return f'''{DESIGN_RULES}\n\nCLIENT BRIEF:\n{brief}\n\nReturn a professional build dossier with: 1) brand/experience thesis, 2) audience and conversion goal, 3) visual direction and anti-template choices, 4) typography system, 5) color/material system, 6) page architecture, 7) component system, 8) motion language, 9) responsive behavior, 10) accessibility/performance requirements, 11) recommended stack, 12) implementation plan, 13) visual QA checklist. Be concrete and opinionated.'''

def install_web_studio_v14():
    if getattr(UltronBrain,'_web_studio_v14',False): return
    old=UltronBrain.handle
    def handle(self,raw):
        text=raw.strip(); low=text.lower()
        if low.startswith('new website '):
            brief=text[len('new website '):].strip(); name=(re.split(r'[:,-]',brief,1)[0] or 'Website')[:80]; now=time.time()
            with _db() as db: cur=db.execute('INSERT INTO projects(name,brief,status,created,updated) VALUES(?,?,?,?,?)',(name,brief,'BRIEF',now,now)); pid=cur.lastrowid
            self.memory.set_setting('ultron_web_active_project',str(pid))
            return AssistantReply(f'WEB STUDIO // PROJECT #{pid}\n{name}\nBrief captured. Say "design website" to generate the premium design dossier.','status')
        if low in {'design website','website design dossier','web studio build plan'}:
            pid=int(self.memory.get_setting('ultron_web_active_project','0') or 0)
            with _db() as db: row=db.execute('SELECT brief FROM projects WHERE id=?',(pid,)).fetchone()
            if not row:return AssistantReply('No active website project. Use: new website <brief>','error')
            prompt=_studio_prompt(row[0]); self.memory.set_setting('ultron_web_pending_prompt',prompt)
            return AssistantReply('WEB STUDIO // DESIGN BRIEF READY\nI prepared the senior-level design/build prompt for the active project. Send: "run website architect" to route it through the AI provider.','status')
        if low=='run website architect':
            prompt=self.memory.get_setting('ultron_web_pending_prompt','')
            if not prompt:return AssistantReply('No pending web architecture prompt.','error')
            # Route through the existing assistant pipeline instead of executing arbitrary code.
            return old(self,prompt)
        if low.startswith('review website '):
            payload=text[len('review website '):]; score,notes=_quality_score(payload); pid=int(self.memory.get_setting('ultron_web_active_project','0') or 0)
            with _db() as db: db.execute('INSERT INTO reviews(project_id,score,notes,created) VALUES(?,?,?,?)',(pid,score,'; '.join(notes),time.time()))
            verdict='PREMIUM' if score>=85 else ('NEEDS POLISH' if score>=70 else 'TEMPLATE RISK')
            return AssistantReply(f'WEB QA // {verdict}\nQUALITY SCORE // {score}/100\n'+('\n'.join(notes) if notes else 'No obvious template-pattern penalties detected.'),'status')
        if low in {'web studio status','website projects'}:
            with _db() as db: rows=db.execute('SELECT id,name,status FROM projects ORDER BY updated DESC LIMIT 8').fetchall()
            return AssistantReply('WEB STUDIO // PROJECTS\n'+('\n'.join(f'#{i} {n} // {s}' for i,n,s in rows) if rows else 'No projects yet.'),'status')
        return old(self,raw)
    UltronBrain.handle=handle;UltronBrain._web_studio_v14=True