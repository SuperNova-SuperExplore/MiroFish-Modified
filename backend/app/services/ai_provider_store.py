"""Local AI provider/model registry.

Stores user-configured OpenAI-compatible providers so deployments can bring their
own 9router/custom API/token/model without editing code.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import Config


DB_PATH = Path(Config.UPLOAD_FOLDER).parent / "uploads" / "ai_providers.sqlite"


class AIProviderStore:
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
                CREATE TABLE IF NOT EXISTS ai_providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    provider_type TEXT NOT NULL DEFAULT 'openai_compatible',
                    base_url TEXT NOT NULL,
                    api_key TEXT,
                    auth_type TEXT NOT NULL DEFAULT 'api_key',
                    default_model TEXT NOT NULL,
                    models_json TEXT,
                    is_active INTEGER NOT NULL DEFAULT 0,
                    notes TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ai_providers_active ON ai_providers(is_active)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ai_providers_name ON ai_providers(name)")
            conn.commit()
        cls._initialized = True

    @classmethod
    def list(cls, include_secrets: bool = False) -> List[Dict[str, Any]]:
        cls.ensure_db()
        with cls._connect() as conn:
            rows = conn.execute("SELECT * FROM ai_providers ORDER BY is_active DESC, updated_at DESC, id DESC").fetchall()
        return [cls._row_to_dict(row, include_secrets=include_secrets) for row in rows]

    @classmethod
    def get(cls, provider_id: str, include_secrets: bool = False) -> Optional[Dict[str, Any]]:
        cls.ensure_db()
        with cls._connect() as conn:
            row = conn.execute("SELECT * FROM ai_providers WHERE provider_id = ?", (provider_id,)).fetchone()
        return cls._row_to_dict(row, include_secrets=include_secrets) if row else None

    @classmethod
    def get_active(cls, include_secrets: bool = True) -> Optional[Dict[str, Any]]:
        cls.ensure_db()
        with cls._connect() as conn:
            row = conn.execute("SELECT * FROM ai_providers WHERE is_active = 1 ORDER BY updated_at DESC, id DESC LIMIT 1").fetchone()
        return cls._row_to_dict(row, include_secrets=include_secrets) if row else None

    @classmethod
    def upsert(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        cls.ensure_db()
        provider_id = payload.get("provider_id") or f"provider_{uuid.uuid4().hex[:12]}"
        existing = cls.get(provider_id, include_secrets=True)
        api_key = payload.get("api_key")
        if existing and (api_key is None or api_key == "" or api_key == "********"):
            api_key = existing.get("api_key")

        name = str(payload.get("name") or provider_id).strip()[:120]
        base_url = cls._normalize_base_url(str(payload.get("base_url") or "").strip())
        default_model = str(payload.get("default_model") or payload.get("model") or "").strip()
        if not base_url:
            raise ValueError("base_url wajib diisi")
        if not default_model:
            raise ValueError("default_model wajib diisi")

        models = payload.get("models") or []
        if isinstance(models, str):
            models = [m.strip() for m in models.split(',') if m.strip()]
        if not isinstance(models, list):
            models = []
        models = [str(m).strip() for m in models if str(m).strip()]
        if default_model not in models:
            models.insert(0, default_model)

        values = (
            provider_id,
            name,
            str(payload.get("provider_type") or "openai_compatible"),
            base_url,
            api_key,
            str(payload.get("auth_type") or "api_key"),
            default_model,
            json.dumps(models, ensure_ascii=False),
            str(payload.get("notes") or "")[:2000],
        )
        with cls._connect() as conn:
            conn.execute(
                """
                INSERT INTO ai_providers (
                    provider_id, name, provider_type, base_url, api_key, auth_type,
                    default_model, models_json, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(provider_id) DO UPDATE SET
                    name = excluded.name,
                    provider_type = excluded.provider_type,
                    base_url = excluded.base_url,
                    api_key = excluded.api_key,
                    auth_type = excluded.auth_type,
                    default_model = excluded.default_model,
                    models_json = excluded.models_json,
                    notes = excluded.notes,
                    updated_at = CURRENT_TIMESTAMP
                """,
                values,
            )
            conn.commit()
        if payload.get("is_active"):
            cls.set_active(provider_id)
        return cls.get(provider_id) or {"provider_id": provider_id}

    @classmethod
    def set_active(cls, provider_id: str) -> Optional[Dict[str, Any]]:
        cls.ensure_db()
        if not cls.get(provider_id, include_secrets=True):
            return None
        with cls._connect() as conn:
            conn.execute("UPDATE ai_providers SET is_active = 0")
            conn.execute(
                "UPDATE ai_providers SET is_active = 1, updated_at = CURRENT_TIMESTAMP WHERE provider_id = ?",
                (provider_id,),
            )
            conn.commit()
        return cls.get(provider_id)

    @classmethod
    def delete(cls, provider_id: str) -> bool:
        cls.ensure_db()
        with cls._connect() as conn:
            cur = conn.execute("DELETE FROM ai_providers WHERE provider_id = ?", (provider_id,))
            conn.commit()
            return cur.rowcount > 0

    @classmethod
    def resolve_active_or_env(cls) -> Dict[str, Any]:
        active = cls.get_active(include_secrets=True)
        if active:
            return active
        return {
            "provider_id": "env",
            "name": "Environment",
            "provider_type": "openai_compatible",
            "base_url": Config.LLM_BASE_URL,
            "api_key": Config.LLM_API_KEY,
            "auth_type": "api_key",
            "default_model": Config.LLM_MODEL_NAME,
            "models": [Config.LLM_MODEL_NAME] if Config.LLM_MODEL_NAME else [],
            "is_active": True,
        }

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        if not base_url:
            return ""
        base_url = base_url.rstrip('/')
        if not base_url.endswith('/v1'):
            base_url = f"{base_url}/v1"
        return base_url

    @staticmethod
    def _mask_secret(secret: Optional[str]) -> Optional[str]:
        if not secret:
            return None
        if len(secret) <= 10:
            return secret[:2] + "***"
        return secret[:8] + "***" + secret[-4:]

    @classmethod
    def _row_to_dict(cls, row: sqlite3.Row, include_secrets: bool = False) -> Dict[str, Any]:
        data = dict(row)
        raw_models = data.pop("models_json", None)
        try:
            data["models"] = json.loads(raw_models) if raw_models else []
        except json.JSONDecodeError:
            data["models"] = []
        data["is_active"] = bool(data.get("is_active"))
        if not include_secrets:
            data["api_key_masked"] = cls._mask_secret(data.get("api_key"))
            data.pop("api_key", None)
        return data
