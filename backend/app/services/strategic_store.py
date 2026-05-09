"""SQLite storage for strategic mode operations."""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import Config


DB_PATH = Path(Config.UPLOAD_FOLDER).parent / "uploads" / "strategic_ops.sqlite"


class StrategicOperationStore:
    """Persist prediction/blueprint operations for UI history and chained flows."""

    _initialized = False

    @classmethod
    def _connect(cls) -> sqlite3.Connection:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def ensure_db(cls) -> None:
        if cls._initialized:
            return
        with cls._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS strategic_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT NOT NULL UNIQUE,
                    mode TEXT NOT NULL,
                    title TEXT,
                    status TEXT NOT NULL DEFAULT 'completed',
                    input_json TEXT NOT NULL,
                    output_json TEXT,
                    parent_operation_id TEXT,
                    model TEXT,
                    provider_base_url TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_strategic_ops_mode ON strategic_operations(mode)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_strategic_ops_parent ON strategic_operations(parent_operation_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_strategic_ops_created ON strategic_operations(created_at)")
            conn.commit()
        cls._initialized = True

    @classmethod
    def create(
        cls,
        *,
        mode: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]],
        title: Optional[str] = None,
        parent_operation_id: Optional[str] = None,
        status: str = "completed",
        model: Optional[str] = None,
        provider_base_url: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        cls.ensure_db()
        operation_id = f"op_{uuid.uuid4().hex[:16]}"
        with cls._connect() as conn:
            conn.execute(
                """
                INSERT INTO strategic_operations (
                    operation_id, mode, title, status, input_json, output_json,
                    parent_operation_id, model, provider_base_url, error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    operation_id,
                    mode,
                    title,
                    status,
                    json.dumps(input_data, ensure_ascii=False),
                    json.dumps(output_data, ensure_ascii=False) if output_data is not None else None,
                    parent_operation_id,
                    model,
                    provider_base_url,
                    error,
                ),
            )
            conn.commit()
        return cls.get(operation_id) or {"operation_id": operation_id}

    @classmethod
    def get(cls, operation_id: str) -> Optional[Dict[str, Any]]:
        cls.ensure_db()
        with cls._connect() as conn:
            row = conn.execute(
                "SELECT * FROM strategic_operations WHERE operation_id = ?",
                (operation_id,),
            ).fetchone()
        return cls._row_to_dict(row) if row else None

    @classmethod
    def list(
        cls,
        *,
        mode: Optional[str] = None,
        parent_operation_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        cls.ensure_db()
        where = []
        params: List[Any] = []
        if mode:
            where.append("mode = ?")
            params.append(mode)
        if parent_operation_id:
            where.append("parent_operation_id = ?")
            params.append(parent_operation_id)
        where_sql = "WHERE " + " AND ".join(where) if where else ""
        params.extend([limit, offset])
        with cls._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM strategic_operations
                {where_sql}
                ORDER BY created_at DESC, id DESC
                LIMIT ? OFFSET ?
                """,
                params,
            ).fetchall()
        return [cls._row_to_dict(row) for row in rows]

    @classmethod
    def delete(cls, operation_id: str) -> bool:
        cls.ensure_db()
        with cls._connect() as conn:
            cur = conn.execute(
                "DELETE FROM strategic_operations WHERE operation_id = ?",
                (operation_id,),
            )
            conn.commit()
            return cur.rowcount > 0

    @classmethod
    def children(cls, operation_id: str) -> List[Dict[str, Any]]:
        return cls.list(parent_operation_id=operation_id, limit=100, offset=0)

    @classmethod
    def _row_to_dict(cls, row: sqlite3.Row) -> Dict[str, Any]:
        data = dict(row)
        for key in ("input_json", "output_json"):
            raw = data.pop(key, None)
            out_key = "input" if key == "input_json" else "output"
            if raw:
                try:
                    data[out_key] = json.loads(raw)
                except json.JSONDecodeError:
                    data[out_key] = raw
            else:
                data[out_key] = None
        return data


def title_from_output(mode: str, output: Dict[str, Any], fallback: str = "Strategic operation") -> str:
    if not isinstance(output, dict):
        return fallback
    if output.get("title"):
        return str(output["title"])
    if mode == "project_prediction":
        return str(output.get("project_summary") or fallback)[:120]
    if mode == "question_prediction":
        return str(output.get("direct_answer") or output.get("prediction") or fallback)[:120]
    if mode == "blueprint_audit":
        verdict = output.get("verdict", "audit")
        score = output.get("score", "-")
        return f"Audit: {verdict} ({score})"
    if mode == "blueprint_revision":
        revised = output.get("revised_blueprint") or {}
        if isinstance(revised, dict) and revised.get("title"):
            return f"Revision: {revised['title']}"
    return fallback
