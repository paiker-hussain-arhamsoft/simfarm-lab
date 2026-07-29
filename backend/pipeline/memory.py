"""Pipeline memory — persists conversation history to SQLite."""

from __future__ import annotations

import json
import os
import sqlite3
import time
from typing import Optional


DB_PATH = os.environ.get("BRAIN_DB_PATH", os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "brain.db"
))


class PipelineMemory:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or DB_PATH
        self._ensure_tables()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self) -> None:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    run_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    task TEXT NOT NULL,
                    history TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_runs_session
                ON pipeline_runs(session_id)
            """)

    def save_run(self, session_id: str, run_id: str, task: str, history: list[dict]) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO pipeline_runs (run_id, session_id, task, history, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (run_id, session_id, task, json.dumps(history), time.time()),
            )

    def get_runs(self, session_id: str) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT run_id, task, history, created_at FROM pipeline_runs "
                "WHERE session_id = ? ORDER BY created_at DESC",
                (session_id,),
            ).fetchall()
        return [
            {
                "run_id": r["run_id"],
                "task": r["task"],
                "history": json.loads(r["history"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def get_run(self, run_id: str) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT run_id, session_id, task, history, created_at FROM pipeline_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "run_id": row["run_id"],
            "session_id": row["session_id"],
            "task": row["task"],
            "history": json.loads(row["history"]),
            "created_at": row["created_at"],
        }

    def get_stats(self) -> dict:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0]
            sessions = conn.execute("SELECT COUNT(DISTINCT session_id) FROM pipeline_runs").fetchone()[0]
        return {"total_runs": total, "unique_sessions": sessions}
