from __future__ import annotations

import hashlib
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from ultron_core import AssistantReply, DATA_DIR, UltronBrain

DB = DATA_DIR / "learning.db"


def _db() -> sqlite3.Connection:
    db = sqlite3.connect(DB, timeout=10)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS command_learning(
            normalized TEXT PRIMARY KEY,
            sample TEXT NOT NULL,
            uses INTEGER NOT NULL DEFAULT 0,
            successes INTEGER NOT NULL DEFAULT 0,
            failures INTEGER NOT NULL DEFAULT 0,
            avg_ms REAL NOT NULL DEFAULT 0,
            last_used TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS error_learning(
            signature TEXT PRIMARY KEY,
            error_type TEXT NOT NULL,
            message TEXT NOT NULL,
            context TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 1,
            recovered INTEGER NOT NULL DEFAULT 0,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS preferences(
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 0.5,
            observations INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL
        );
        """
    )
    return db


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\b\d+(?:\.\d+)?\b", "#", text)
    return re.sub(r"\s+", " ", text).strip(" .!?¿¡,;:")[:220]


def record_command(text: str, success: bool, elapsed_ms: float = 0.0) -> None:
    norm = normalize(text)
    if not norm:
        return
    now = datetime.now().isoformat(timespec="seconds")
    with _db() as db:
        row = db.execute("SELECT uses,avg_ms FROM command_learning WHERE normalized=?", (norm,)).fetchone()
        uses = int(row[0]) if row else 0
        avg = float(row[1]) if row else 0.0
        new_avg = elapsed_ms if uses == 0 else ((avg * uses) + elapsed_ms) / (uses + 1)
        db.execute(
            """INSERT INTO command_learning(normalized,sample,uses,successes,failures,avg_ms,last_used)
               VALUES(?,?,1,?,?,?,?)
               ON CONFLICT(normalized) DO UPDATE SET
                 sample=excluded.sample,
                 uses=command_learning.uses+1,
                 successes=command_learning.successes+excluded.successes,
                 failures=command_learning.failures+excluded.failures,
                 avg_ms=excluded.avg_ms,
                 last_used=excluded.last_used""",
            (norm, text[:300], int(success), int(not success), new_avg, now),
        )


def record_error(exc: BaseException | str, context: str = "runtime", recovered: bool = False) -> str:
    if isinstance(exc, BaseException):
        etype = type(exc).__name__
        message = str(exc)
    else:
        etype = "Error"
        message = str(exc)
    clean = re.sub(r"0x[0-9a-fA-F]+", "0x*", message)[:600]
    signature = hashlib.sha256(f"{etype}|{clean}|{context}".encode("utf-8", "ignore")).hexdigest()[:16]
    now = datetime.now().isoformat(timespec="seconds")
    with _db() as db:
        db.execute(
            """INSERT INTO error_learning(signature,error_type,message,context,count,recovered,first_seen,last_seen)
               VALUES(?,?,?,?,1,?,?,?)
               ON CONFLICT(signature) DO UPDATE SET
                 count=error_learning.count+1,
                 recovered=error_learning.recovered+excluded.recovered,
                 message=excluded.message,
                 last_seen=excluded.last_seen""",
            (signature, etype, clean, context[:160], int(recovered), now, now),
        )
    return signature


def observe_preference(key: str, value: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    with _db() as db:
        row = db.execute("SELECT value,confidence,observations FROM preferences WHERE key=?", (key,)).fetchone()
        if row and row[0] == value:
            observations = int(row[2]) + 1
            confidence = min(0.98, float(row[1]) + 0.06)
        else:
            observations = 1 if not row else int(row[2]) + 1
            confidence = 0.55 if not row else max(0.35, float(row[1]) - 0.12)
        db.execute(
            "INSERT INTO preferences(key,value,confidence,observations,updated_at) VALUES(?,?,?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value,confidence=excluded.confidence,observations=excluded.observations,updated_at=excluded.updated_at",
            (key, value, confidence, observations, now),
        )


def learning_summary() -> str:
    with _db() as db:
        commands, uses, successes, failures = db.execute(
            "SELECT COUNT(*),COALESCE(SUM(uses),0),COALESCE(SUM(successes),0),COALESCE(SUM(failures),0) FROM command_learning"
        ).fetchone()
        errors, repeats, recovered = db.execute(
            "SELECT COUNT(*),COALESCE(SUM(CASE WHEN count>1 THEN 1 ELSE 0 END),0),COALESCE(SUM(recovered),0) FROM error_learning"
        ).fetchone()
        prefs = db.execute("SELECT COUNT(*) FROM preferences WHERE confidence>=0.7").fetchone()[0]
    return (
        f"SELF LEARNING // ONLINE\nPATTERNS // {commands}\nOBSERVATIONS // {uses}\nSUCCESS // {successes}\nFAILURES // {failures}\n"
        f"ERROR SIGNATURES // {errors}\nREPEATING ERRORS // {repeats}\nRECOVERIES // {recovered}\nCONFIDENT PREFERENCES // {prefs}"
    )


def learned_insights(limit: int = 6) -> list[str]:
    out: list[str] = []
    with _db() as db:
        for sample, uses, ok, fail, avg in db.execute(
            "SELECT sample,uses,successes,failures,avg_ms FROM command_learning ORDER BY uses DESC,last_used DESC LIMIT ?", (limit,)
        ).fetchall():
            rate = int((ok / max(1, ok + fail)) * 100)
            out.append(f"COMMAND // {sample[:70]} // {uses}x // {rate}% success // {avg:.0f} ms")
        for etype, message, count, recovered in db.execute(
            "SELECT error_type,message,count,recovered FROM error_learning ORDER BY count DESC,last_seen DESC LIMIT 3"
        ).fetchall():
            out.append(f"ERROR // {etype} x{count} // recovered {recovered}x // {message[:80]}")
    return out


def install_learning_v10() -> None:
    if getattr(UltronBrain, "_learning_v10", False):
        return
    _db().close()
    original = UltronBrain.handle

    def handle(self: UltronBrain, raw: str) -> AssistantReply:
        low = raw.lower().strip(" .!?¿¡")
        if low in {"learning status", "self learning status", "estado aprendizaje", "learning core"}:
            return AssistantReply(learning_summary(), "status")
        if low in {"what have you learned", "que has aprendido", "qué has aprendido", "learned insights"}:
            items = learned_insights()
            return AssistantReply("LEARNED INSIGHTS\n" + ("\n".join(items) if items else "No observations yet."), "status")
        if low in {"error learning", "error learning status", "estado errores"}:
            with _db() as db:
                rows = db.execute("SELECT error_type,message,count,recovered FROM error_learning ORDER BY count DESC,last_seen DESC LIMIT 6").fetchall()
            lines = [f"{t} // x{c} // recovered {r} // {m[:100]}" for t,m,c,r in rows]
            return AssistantReply("ERROR LEARNING // ONLINE\n" + ("\n".join(lines) if lines else "No learned errors yet."), "status")

        # Learn stable preferences only from explicit mode choices, never from secrets or arbitrary content.
        pref_map = {
            "gaming mode": ("preferred_profile", "gaming"),
            "study mode": ("preferred_profile", "study"),
            "cinematic mode": ("preferred_profile", "cinematic"),
            "focus mode": ("preferred_focus", "on"),
            "performance mode": ("preferred_performance", "on"),
        }
        if low in pref_map:
            observe_preference(*pref_map[low])
        return original(self, raw)

    UltronBrain.handle = handle
    UltronBrain._learning_v10 = True
