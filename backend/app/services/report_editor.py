"""Targeted report editor with backups."""

from __future__ import annotations

import json
import os
import re
import shutil
import uuid
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
    def _log_path(report_id: str) -> str:
        return os.path.join(ReportManager._get_report_folder(report_id), 'edit_log.jsonl')

    @staticmethod
    def _append_log(report_id: str, event: Dict[str, Any]):
        folder = ReportManager._get_report_folder(report_id)
        os.makedirs(folder, exist_ok=True)
        payload = {
            'ts': datetime.now().isoformat(),
            **event,
        }
        with open(ReportEditor._log_path(report_id), 'a', encoding='utf-8') as f:
            f.write(json.dumps(payload, ensure_ascii=False) + '\n')

    @staticmethod
    def get_edit_logs(report_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        path = ReportEditor._log_path(report_id)
        if not os.path.exists(path):
            return []
        logs = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return logs[-limit:]

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
        range_matches = list(re.finditer(r'(\d{1,3})\s*[-–]\s*(\d{1,3})\s*%', instruction))
        if range_matches:
            target_match = range_matches[-1]
            target_value = f"{target_match.group(1)}-{target_match.group(2)}%"
        else:
            single_matches = list(re.finditer(r'(\d{1,3})\s*%', instruction))
            target_single = single_matches[-1] if single_matches else None
            target_value = f"{target_single.group(1)}%" if target_single else None
        if not target_value:
            return []

        exact_line_match = re.search(r'(Temuan\s+\d+\s+[–-]\s+[^\n]+?confidence\s+)\d{1,3}(%\))', instruction, re.IGNORECASE)
        if exact_line_match:
            old_line_match = re.search(r'(Temuan\s+\d+\s+[–-]\s+[^\n]+?confidence\s+\d{1,3}%\)\.)', markdown, re.IGNORECASE)
            if old_line_match:
                old = old_line_match.group(1)
                new = re.sub(r'(confidence\s+)\d{1,3}%', rf'\g<1>{target_value}', old, count=1, flags=re.IGNORECASE)
                replacements.append({'old': old, 'new': new})
                # Also update matching confidence note if present.
                note_old = f'Skor {old.split("confidence ")[-1].replace(").", "").replace(".", "")} dan tiga kelemahan utama'
                if note_old in markdown:
                    replacements.append({'old': note_old, 'new': f'Skor {target_value} dan tiga kelemahan utama'})
                return replacements

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
    def _load_rendered_sections(report_id: str) -> str:
        folder = ReportManager._get_report_folder(report_id)
        if not os.path.exists(folder):
            return ''
        chunks = []
        for filename in sorted(os.listdir(folder)):
            if filename.startswith('section_') and filename.endswith('.md'):
                path = os.path.join(folder, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    chunks.append(f'\n\n<!-- {filename} -->\n' + f.read())
        return ''.join(chunks)

    @staticmethod
    def _llm_propose_replacements(full_markdown: str, section_markdown: str, instruction: str, report_id: str = '', edit_id: str = '') -> List[Dict[str, str]]:
        full_clipped = full_markdown[:22000]
        sections_clipped = section_markdown[:22000]
        system = """Kamu adalah AI editor dokumen Markdown.
Kamu HARUS membaca dokumen, memahami instruksi user, menentukan lokasi edit yang benar, lalu menghasilkan replacement kecil yang bisa dieksekusi sistem.
Balas JSON valid saja: {"replacements":[{"old":"teks persis yang ada di dokumen","new":"teks pengganti","reason":"kenapa bagian ini dipilih"}],"needs_confirmation":false,"reason":"..."}
Aturan keras:
- Kamu yang menentukan lokasi edit dari makna instruksi, bukan keyword statis.
- old harus teks persis yang muncul di FULL_REPORT atau RENDERED_SECTIONS.
- Kalau panel/tampilan kiri berbeda dari full report, prioritaskan RENDERED_SECTIONS karena itu yang user lihat.
- Maksimal 3 replacements.
- Jangan rewrite seluruh dokumen.
- Jangan mengaku tidak punya akses tulis; backend akan mengeksekusi replacement kamu.
- Kalau target benar-benar ambigu, replacements kosong dan needs_confirmation true."""
        user = f"""INSTRUKSI USER:
{instruction}

FULL_REPORT_MD:
{full_clipped}

RENDERED_SECTIONS_MD_YANG_DILIHAT_USER:
{sections_clipped}"""
        try:
            result = LLMClient(task_type='report_editor').chat_json(
                messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
                temperature=0.0,
            )
        except Exception as first_error:
            if report_id:
                ReportEditor._append_log(report_id, {
                    'edit_id': edit_id,
                    'stage': 'llm_error',
                    'error': str(first_error),
                    'retry': 'compact_context',
                })
            compact_user = f"""INSTRUKSI USER:
{instruction}

RENDERED_SECTIONS_MD_YANG_DILIHAT_USER:
{section_markdown[:12000]}

TUGAS: cari teks target di section di atas dan balas JSON replacement valid."""
            try:
                result = LLMClient(task_type='report_editor').chat_json(
                    messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': compact_user}],
                    temperature=0.0,
                )
            except Exception as second_error:
                if report_id:
                    ReportEditor._append_log(report_id, {
                        'edit_id': edit_id,
                        'stage': 'llm_error_final',
                        'error': str(second_error),
                    })
                return []
        reps = result.get('replacements', []) if isinstance(result, dict) else []
        clean = []
        for rep in reps[:3]:
            old = rep.get('old')
            new = rep.get('new')
            if isinstance(old, str) and isinstance(new, str) and old and old != new:
                clean.append({'old': old, 'new': new})
        return clean

    @staticmethod
    def _count_in_section_files(report_id: str, text: str) -> int:
        folder = ReportManager._get_report_folder(report_id)
        if not os.path.exists(folder):
            return 0
        total = 0
        for filename in os.listdir(folder):
            if not (filename.startswith('section_') and filename.endswith('.md')):
                continue
            path = os.path.join(folder, filename)
            with open(path, 'r', encoding='utf-8') as f:
                total += f.read().count(text)
        return total

    @staticmethod
    def _apply_replacements_to_section_files(report_id: str, replacements: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        folder = ReportManager._get_report_folder(report_id)
        writes = []
        if not os.path.exists(folder):
            return writes
        for filename in os.listdir(folder):
            if not (filename.startswith('section_') and filename.endswith('.md')):
                continue
            path = os.path.join(folder, filename)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = content
            changed = False
            for rep in replacements:
                if rep['old'] in new_content:
                    new_content = new_content.replace(rep['old'], rep['new'], 1)
                    changed = True
            if changed:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                writes.append({'filename': filename, 'path': path})
        return writes

    @staticmethod
    def apply_instruction(report_id: str, instruction: str) -> Dict[str, Any]:
        edit_id = f"edit_{uuid.uuid4().hex[:10]}"
        markdown = ReportEditor._load_markdown(report_id)
        section_markdown = ReportEditor._load_rendered_sections(report_id)
        ReportEditor._append_log(report_id, {
            'edit_id': edit_id,
            'stage': 'start',
            'instruction': instruction,
            'full_report_chars': len(markdown),
            'section_chars': len(section_markdown),
        })
        replacements = ReportEditor._llm_propose_replacements(markdown, section_markdown, instruction, report_id=report_id, edit_id=edit_id)
        ReportEditor._append_log(report_id, {
            'edit_id': edit_id,
            'stage': 'llm_proposal',
            'replacement_count': len(replacements),
            'replacements': replacements,
        })
        fallback_used = False
        if not replacements:
            replacements = ReportEditor._deterministic_percentage_patch(markdown + '\n' + section_markdown, instruction)
            fallback_used = bool(replacements)
            ReportEditor._append_log(report_id, {
                'edit_id': edit_id,
                'stage': 'fallback_proposal',
                'replacement_count': len(replacements),
                'replacements': replacements,
            })

        if not replacements:
            ReportEditor._append_log(report_id, {
                'edit_id': edit_id,
                'stage': 'no_replacements',
                'message': 'Target edit belum cukup jelas atau teks target tidak ditemukan.',
            })
            return {
                'changed': False,
                'needs_confirmation': True,
                'message': 'Target edit belum cukup jelas atau teks target tidak ditemukan.',
                'replacements': [],
            }

        # Validate uniqueness and apply sequentially. Some reports render from
        # section_XX.md; full_report.md may already be edited while section files
        # are stale, so allow section-only replacements when full has 0 matches
        # but exactly one section has the target.
        new_markdown = markdown
        applied = []
        full_changed = False
        section_only = []
        for rep in replacements:
            old = rep['old']
            new = rep['new']
            count = new_markdown.count(old)
            section_count = ReportEditor._count_in_section_files(report_id, old)
            ReportEditor._append_log(report_id, {
                'edit_id': edit_id,
                'stage': 'validate_replacement',
                'old_preview': old[:240],
                'new_preview': new[:240],
                'full_match_count': count,
                'section_match_count': section_count,
            })
            if count == 1:
                new_markdown = new_markdown.replace(old, new, 1)
                full_changed = True
                applied.append({'old': old, 'new': new})
            elif count == 0 and section_count == 1:
                section_only.append({'old': old, 'new': new})
                applied.append({'old': old, 'new': new})
            else:
                ReportEditor._append_log(report_id, {
                    'edit_id': edit_id,
                    'stage': 'validation_failed',
                    'full_match_count': count,
                    'section_match_count': section_count,
                    'old_preview': old[:500],
                })
                return {
                    'changed': False,
                    'needs_confirmation': True,
                    'message': f'Teks target tidak unik/ditemukan {count} kali di full report dan {section_count} kali di section files: {old[:120]}',
                    'replacements': applied,
                }

        backups = ReportEditor._backup(report_id)
        section_writes = ReportEditor._apply_replacements_to_section_files(report_id, applied)
        full_written = False
        if full_changed:
            ReportEditor._save_markdown(report_id, new_markdown)
            full_written = True
        ReportEditor._append_log(report_id, {
            'edit_id': edit_id,
            'stage': 'written',
            'full_written': full_written,
            'section_writes': section_writes,
            'backup': backups,
            'applied_count': len(applied),
        })
        return {
            'changed': True,
            'needs_confirmation': False,
            'message': f'Berhasil menerapkan {len(applied)} perubahan targeted.',
            'mode': 'llm_first_with_safe_validation',
            'fallback_used': fallback_used,
            'replacements': applied,
            'backup': backups,
            'edit_id': edit_id,
            'section_writes': section_writes,
            'full_written': full_written,
        }
