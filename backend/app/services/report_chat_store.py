"""Persistent report chat history."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List

from ..config import Config

CHAT_DIR = os.path.join(Config.UPLOAD_FOLDER, 'report_chats')


def _ensure_dir():
    os.makedirs(CHAT_DIR, exist_ok=True)


def _path(report_id: str) -> str:
    _ensure_dir()
    safe = ''.join(c for c in report_id if c.isalnum() or c in {'_', '-'})
    return os.path.join(CHAT_DIR, f'{safe}.json')


class ReportChatStore:
    @staticmethod
    def get(report_id: str) -> List[Dict[str, Any]]:
        path = _path(report_id)
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    @staticmethod
    def append(report_id: str, role: str, content: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        item = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'meta': meta or {},
        }
        history = ReportChatStore.get(report_id)
        history.append(item)
        with open(_path(report_id), 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return item

    @staticmethod
    def clear(report_id: str):
        path = _path(report_id)
        if os.path.exists(path):
            os.remove(path)
