"""Targeted report editor with backups."""

from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime
from typing import Any, Dict, List

from .report_agent import ReportManager
from ..utils.llm_client import LLMClient


def _timestamp() -> str:
    return datetime.now().strftime('%Y%m%d-%H%M%S')


def _is_draft_like_instruction(instruction: str) -> bool:
    text = (instruction or '').lower()
    return 'draft perubahan' in text or 'lokasi:' in text or 'ubah menjadi' in text


class ReportEditor:
    @staticmethod
    def _backup(report_id: str) -> Dict[str, str]:
        folder = ReportManager._get_report_folder(report_id)
        ts = _timestamp()
        backups = {}
        for name in ['full_report.md', 'meta.json']:
            src = os.path.join(folder, name)
            if os.path.exists(src):
                dst = os.path.join(folder, f'{name}.bak.{ts}')
                shutil.copy2(src, dst)
                backups[name] = dst
        return backups

    @staticmethod
    def _load_markdown(report_id: str) -> str:
        report = ReportManager.get_report(report_id)
        if not report:
            raise ValueError(f'Laporan tidak ditemukan: {report_id}')
        return report.markdown_content or ''

    @staticmethod
    def _save_markdown(report_id: str, markdown: str):
        report = ReportManager.get_report(report_id)
        if not report:
            raise ValueError(f'Laporan tidak ditemukan: {report_id}')
        report.markdown_content = markdown
        ReportManager.save_report(report)

    @staticmethod
    def _deterministic_percentage_patch(markdown: str, instruction: str) -> List[Dict[str, str]]:
        """Handle common percentage/confidence edits safely."""
        text = instruction.lower()
        replacements = []
        target_match = re.search(r'(\d{1,3})\s*[-–]\s*(\d{1,3})\s*%', instruction)
        if not target_match:
            target_single = re.search(r'(\d{1,3})\s*%', instruction)
            target_value = f"{target_single.group(1)}%" if target_single else None
        else:
            target_value = f"{target_match.group(1)}-{target_match.group(2)}%"
        if not target_value:
            return []

        if any(k in text for k in ['personalisasi', 'kontrol', 'data personal', 'critical risks', 'hidden assumptions']):
            candidates = [
                (
                    '🟢 Risiko personalisasi dan kontrol – confidence 82-85% (konsisten dari tiga alat).',
                    f'🟢 Risiko personalisasi dan kontrol – confidence {target_value} (konsisten dari tiga alat).'
                ),
                (
                    '🟢 Risiko personalisasi dan kontrol – confidence 82–85% (konsisten dari tiga alat).',
                    f'🟢 Risiko personalisasi dan kontrol – confidence {target_value} (konsisten dari tiga alat).'
                ),
                (
                    '| Data personal tidak tersedia | Konten terasa rusak, balik arah | 🟢 85% | Tambah konten fallback generik hangat |',
                    f'| Data personal tidak tersedia | Konten terasa rusak, balik arah | 🟢 {target_value} | Tambah konten fallback generik hangat |'
                ),
            ]
            for old, new in candidates:
                if old in markdown and old != new:
                    replacements.append({'old': old, 'new': new})
        return replacements

    @staticmethod
    def _llm_propose_replacements(markdown: str, instruction: str) -> List[Dict[str, str]]:
        clipped = markdown[:28000]
        system = """Kamu adalah editor dokumen Markdown yang sangat hati-hati.
Tugasmu menghasilkan replacement kecil dan presisi.
Balas JSON valid: {"replacements":[{"old":"teks persis yang ada di dokumen","new":"teks pengganti"}],"needs_confirmation":false,"reason":"..."}
Aturan:
- Jangan rewrite seluruh dokumen.
- old harus teks persis dari dokumen.
- Maksimal 3 replacements.
- Kalau target ambigu, replacements kosong dan needs_confirmation true.
- Jangan hapus section lain."""
        user = f"""INSTRUKSI EDIT:
{instruction}

DOKUMEN MARKDOWN:
{clipped}"""
        result = LLMClient(task_type='report_editor').chat_json(
            messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
            temperature=0.0,
        )
        reps = result.get('replacements', []) if isinstance(result, dict) else []
        clean = []
        for rep in reps[:3]:
            old = rep.get('old')
            new = rep.get('new')
            if isinstance(old, str) and isinstance(new, str) and old and old != new:
                clean.append({'old': old, 'new': new})
        return clean

    @staticmethod
    def apply_instruction(report_id: str, instruction: str) -> Dict[str, Any]:
        markdown = ReportEditor._load_markdown(report_id)
        replacements = ReportEditor._deterministic_percentage_patch(markdown, instruction)
        if not replacements and not _is_draft_like_instruction(instruction):
            replacements = ReportEditor._llm_propose_replacements(markdown, instruction)

        if not replacements:
            return {
                'changed': False,
                'needs_confirmation': True,
                'message': 'Target edit belum cukup jelas atau teks target tidak ditemukan.',
                'replacements': [],
            }

        # Validate uniqueness and apply sequentially.
        new_markdown = markdown
        applied = []
        for rep in replacements:
            old = rep['old']
            new = rep['new']
            count = new_markdown.count(old)
            if count != 1:
                return {
                    'changed': False,
                    'needs_confirmation': True,
                    'message': f'Teks target tidak unik/ditemukan {count} kali: {old[:120]}',
                    'replacements': applied,
                }
            new_markdown = new_markdown.replace(old, new, 1)
            applied.append({'old': old, 'new': new})

        backups = ReportEditor._backup(report_id)
        ReportEditor._save_markdown(report_id, new_markdown)
        return {
            'changed': True,
            'needs_confirmation': False,
            'message': f'Berhasil menerapkan {len(applied)} perubahan targeted.',
            'replacements': applied,
            'backup': backups,
        }
