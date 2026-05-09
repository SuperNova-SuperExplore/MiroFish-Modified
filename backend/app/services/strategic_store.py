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
                    tags_json TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cls._ensure_column(conn, "strategic_operations", "tags_json", "TEXT")
            cls._ensure_column(conn, "strategic_operations", "notes", "TEXT")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_strategic_ops_mode ON strategic_operations(mode)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_strategic_ops_parent ON strategic_operations(parent_operation_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_strategic_ops_created ON strategic_operations(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_strategic_ops_title ON strategic_operations(title)")
            conn.commit()
        cls._initialized = True

    @classmethod
    def _ensure_column(cls, conn: sqlite3.Connection, table: str, column: str, column_type: str) -> None:
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        if column not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")

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
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        cls.ensure_db()
        operation_id = f"op_{uuid.uuid4().hex[:16]}"
        with cls._connect() as conn:
            conn.execute(
                """
                INSERT INTO strategic_operations (
                    operation_id, mode, title, status, input_json, output_json,
                    parent_operation_id, model, provider_base_url, error, tags_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    json.dumps(cls._normalize_tags(tags or []), ensure_ascii=False),
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
        q: Optional[str] = None,
        tag: Optional[str] = None,
        status: Optional[str] = None,
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
        if status:
            where.append("status = ?")
            params.append(status)
        if tag:
            where.append("tags_json LIKE ?")
            params.append(f'%"{tag}"%')
        if q:
            like = f"%{q}%"
            where.append("(title LIKE ? OR mode LIKE ? OR input_json LIKE ? OR output_json LIKE ? OR tags_json LIKE ?)")
            params.extend([like, like, like, like, like])
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
    def update_metadata(
        cls,
        operation_id: str,
        *,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        cls.ensure_db()
        updates = []
        params: List[Any] = []
        if title is not None:
            updates.append("title = ?")
            params.append(title.strip()[:200] if isinstance(title, str) else title)
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes.strip()[:10000] if isinstance(notes, str) else notes)
        if status is not None:
            updates.append("status = ?")
            params.append(status.strip()[:40] if isinstance(status, str) else status)
        if not updates:
            return cls.get(operation_id)
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(operation_id)
        with cls._connect() as conn:
            cur = conn.execute(
                f"UPDATE strategic_operations SET {', '.join(updates)} WHERE operation_id = ?",
                params,
            )
            conn.commit()
            if cur.rowcount == 0:
                return None
        return cls.get(operation_id)

    @classmethod
    def update_tags(cls, operation_id: str, tags: List[str]) -> Optional[Dict[str, Any]]:
        cls.ensure_db()
        normalized = cls._normalize_tags(tags)
        with cls._connect() as conn:
            cur = conn.execute(
                """
                UPDATE strategic_operations
                SET tags_json = ?, updated_at = CURRENT_TIMESTAMP
                WHERE operation_id = ?
                """,
                (json.dumps(normalized, ensure_ascii=False), operation_id),
            )
            conn.commit()
            if cur.rowcount == 0:
                return None
        return cls.get(operation_id)

    @classmethod
    def add_tags(cls, operation_id: str, tags: List[str]) -> Optional[Dict[str, Any]]:
        operation = cls.get(operation_id)
        if not operation:
            return None
        current = operation.get("tags") or []
        return cls.update_tags(operation_id, current + tags)

    @classmethod
    def all_tags(cls) -> List[Dict[str, Any]]:
        cls.ensure_db()
        counts: Dict[str, int] = {}
        with cls._connect() as conn:
            rows = conn.execute("SELECT tags_json FROM strategic_operations WHERE tags_json IS NOT NULL").fetchall()
        for row in rows:
            raw = row[0]
            if not raw:
                continue
            try:
                tags = json.loads(raw)
            except json.JSONDecodeError:
                continue
            for tag in tags if isinstance(tags, list) else []:
                counts[tag] = counts.get(tag, 0) + 1
        return [{"tag": tag, "count": count} for tag, count in sorted(counts.items())]

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
        raw_tags = data.pop("tags_json", None)
        if raw_tags:
            try:
                parsed = json.loads(raw_tags)
                data["tags"] = parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                data["tags"] = []
        else:
            data["tags"] = []
        return data

    @staticmethod
    def _normalize_tags(tags: List[str]) -> List[str]:
        normalized = []
        seen = set()
        for tag in tags:
            if not isinstance(tag, str):
                continue
            cleaned = tag.strip().lower().replace(" ", "-")
            cleaned = ''.join(c for c in cleaned if c.isalnum() or c in {'-', '_'})
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                normalized.append(cleaned[:40])
        return normalized[:20]


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
