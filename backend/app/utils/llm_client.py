"""
OpenAI-compatible LLM client with app-level usage logging and prompt cache.

This is intentionally centralized so every MiroFish LLM call gets the same
observability layer without changing individual services.
"""

import hashlib
import json
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from openai import OpenAI

from ..config import Config


DB_PATH = Path(Config.UPLOAD_FOLDER).parent / "uploads" / "llm_usage.sqlite"


class LLMClient:
    """OpenAI-compatible LLM client with usage tracking and deterministic cache."""

    _db_initialized = False

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        task_type: Optional[str] = None,
    ):
        active_provider = None
        if api_key is None and base_url is None and model is None:
            from ..services.ai_provider_store import AIProviderStore
            active_provider = AIProviderStore.resolve_active_or_env()

        self.api_key = api_key or (active_provider or {}).get("api_key") or Config.LLM_API_KEY
        self.base_url = base_url or (active_provider or {}).get("base_url") or Config.LLM_BASE_URL
        self.model = model or (active_provider or {}).get("default_model") or Config.LLM_MODEL_NAME
        self.provider_id = (active_provider or {}).get("provider_id") if active_provider else None
        self.task_type = task_type or "general"

        if not self.api_key:
            raise ValueError("LLM_API_KEY is not configured")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        self._ensure_db()

    @classmethod
    def _connect_db(cls) -> sqlite3.Connection:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(DB_PATH))

    @classmethod
    def _ensure_db(cls) -> None:
        if cls._db_initialized:
            return
        with cls._connect_db() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    provider_base_url TEXT,
                    model TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    prompt_hash TEXT NOT NULL,
                    cache_key TEXT NOT NULL,
                    cached_hit INTEGER NOT NULL DEFAULT 0,
                    success INTEGER NOT NULL DEFAULT 1,
                    error TEXT,
                    latency_ms INTEGER NOT NULL DEFAULT 0,
                    temperature REAL,
                    max_tokens INTEGER,
                    input_chars INTEGER NOT NULL DEFAULT 0,
                    output_chars INTEGER NOT NULL DEFAULT 0,
                    input_tokens_est INTEGER NOT NULL DEFAULT 0,
                    output_tokens_est INTEGER NOT NULL DEFAULT 0,
                    api_prompt_tokens INTEGER,
                    api_completion_tokens INTEGER,
                    api_total_tokens INTEGER
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_cache (
                    cache_key TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    model TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    prompt_hash TEXT NOT NULL,
                    temperature REAL,
                    max_tokens INTEGER,
                    response_format TEXT,
                    input_chars INTEGER NOT NULL DEFAULT 0,
                    output_chars INTEGER NOT NULL DEFAULT 0,
                    content TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_usage_created ON llm_usage(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_usage_model ON llm_usage(model)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_llm_usage_task ON llm_usage(task_type)")
            conn.commit()
        cls._db_initialized = True

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Cheap heuristic. Good enough for estimates without tiktoken dependency."""
        if not text:
            return 0
        # Mixed Indonesian/English/code: about 4 chars per token.
        return max(1, int(len(text) / 4))

    @staticmethod
    def _messages_text(messages: List[Dict[str, str]]) -> str:
        return json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def _cache_enabled(self, temperature: float, response_format: Optional[Dict]) -> bool:
        if os.getenv("LLM_CACHE_ENABLED", "true").lower() not in {"1", "true", "yes", "on"}:
            return False
        if os.getenv("LLM_CACHE_FORCE", "false").lower() in {"1", "true", "yes", "on"}:
            return True
        # Only cache deterministic-ish calls by default.
        return temperature <= float(os.getenv("LLM_CACHE_MAX_TEMPERATURE", "0.3")) or bool(response_format)

    def _make_cache_key(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict],
    ) -> Tuple[str, str, int]:
        messages_text = self._messages_text(messages)
        input_chars = len(messages_text)
        prompt_hash = hashlib.sha256(messages_text.encode("utf-8")).hexdigest()
        payload = {
            "base_url": self.base_url,
            "model": self.model,
            "task_type": self.task_type,
            "messages_hash": prompt_hash,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": response_format or None,
        }
        cache_key = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return cache_key, prompt_hash, input_chars

    def _read_cache(self, cache_key: str) -> Optional[str]:
        with self._connect_db() as conn:
            row = conn.execute("SELECT content FROM llm_cache WHERE cache_key = ?", (cache_key,)).fetchone()
            return row[0] if row else None

    def _write_cache(
        self,
        cache_key: str,
        prompt_hash: str,
        content: str,
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict],
        input_chars: int,
    ) -> None:
        response_format_text = json.dumps(response_format, ensure_ascii=False, sort_keys=True) if response_format else None
        with self._connect_db() as conn:
            conn.execute(
                """
                INSERT INTO llm_cache (
                    cache_key, model, task_type, prompt_hash, temperature, max_tokens,
                    response_format, input_chars, output_chars, content
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    updated_at = CURRENT_TIMESTAMP,
                    output_chars = excluded.output_chars,
                    content = excluded.content
                """,
                (
                    cache_key,
                    self.model,
                    self.task_type,
                    prompt_hash,
                    temperature,
                    max_tokens,
                    response_format_text,
                    input_chars,
                    len(content),
                    content,
                ),
            )
            conn.commit()

    def _log_usage(
        self,
        *,
        prompt_hash: str,
        cache_key: str,
        cached_hit: bool,
        success: bool,
        error: Optional[str],
        latency_ms: int,
        temperature: float,
        max_tokens: int,
        input_chars: int,
        output_chars: int,
        api_usage: Optional[Any] = None,
    ) -> None:
        api_prompt_tokens = None
        api_completion_tokens = None
        api_total_tokens = None
        if api_usage:
            api_prompt_tokens = getattr(api_usage, "prompt_tokens", None)
            api_completion_tokens = getattr(api_usage, "completion_tokens", None)
            api_total_tokens = getattr(api_usage, "total_tokens", None)

        with self._connect_db() as conn:
            conn.execute(
                """
                INSERT INTO llm_usage (
                    provider_base_url, model, task_type, prompt_hash, cache_key,
                    cached_hit, success, error, latency_ms, temperature, max_tokens,
                    input_chars, output_chars, input_tokens_est, output_tokens_est,
                    api_prompt_tokens, api_completion_tokens, api_total_tokens
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.base_url,
                    self.model,
                    self.task_type,
                    prompt_hash,
                    cache_key,
                    1 if cached_hit else 0,
                    1 if success else 0,
                    error,
                    latency_ms,
                    temperature,
                    max_tokens,
                    input_chars,
                    output_chars,
                    self._estimate_tokens("x" * input_chars),
                    self._estimate_tokens("x" * output_chars),
                    api_prompt_tokens,
                    api_completion_tokens,
                    api_total_tokens,
                ),
            )
            conn.commit()

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None,
        task_type: Optional[str] = None,
    ) -> str:
        """Send a chat request and return plain text content."""
        if task_type:
            previous_task_type = self.task_type
            self.task_type = task_type
        else:
            previous_task_type = None

        started = time.time()
        cache_key, prompt_hash, input_chars = self._make_cache_key(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

        try:
            if self._cache_enabled(temperature, response_format):
                cached = self._read_cache(cache_key)
                if cached is not None:
                    latency_ms = int((time.time() - started) * 1000)
                    self._log_usage(
                        prompt_hash=prompt_hash,
                        cache_key=cache_key,
                        cached_hit=True,
                        success=True,
                        error=None,
                        latency_ms=latency_ms,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        input_chars=input_chars,
                        output_chars=len(cached),
                    )
                    return cached

            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""
            content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()
            latency_ms = int((time.time() - started) * 1000)

            if self._cache_enabled(temperature, response_format):
                self._write_cache(
                    cache_key=cache_key,
                    prompt_hash=prompt_hash,
                    content=content,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                    input_chars=input_chars,
                )

            self._log_usage(
                prompt_hash=prompt_hash,
                cache_key=cache_key,
                cached_hit=False,
                success=True,
                error=None,
                latency_ms=latency_ms,
                temperature=temperature,
                max_tokens=max_tokens,
                input_chars=input_chars,
                output_chars=len(content),
                api_usage=getattr(response, "usage", None),
            )
            return content
        except Exception as exc:
            latency_ms = int((time.time() - started) * 1000)
            self._log_usage(
                prompt_hash=prompt_hash,
                cache_key=cache_key,
                cached_hit=False,
                success=False,
                error=str(exc)[:1000],
                latency_ms=latency_ms,
                temperature=temperature,
                max_tokens=max_tokens,
                input_chars=input_chars,
                output_chars=0,
            )
            raise
        finally:
            if previous_task_type is not None:
                self.task_type = previous_task_type

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        task_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a chat request and parse a JSON object response."""
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            task_type=task_type,
        )
        cleaned_response = response.strip()
        cleaned_response = re.sub(r"^```(?:json)?\s*\n?", "", cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r"\n?```\s*$", "", cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"LLM returned invalid JSON: {cleaned_response}")
