"""
Strategic lightweight modes for focused prediction and blueprint workflows.

These modes are intentionally cheaper than the full OASIS social simulation.
They use the centralized LLMClient so usage logging and prompt cache apply.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ..utils.llm_client import LLMClient


class StrategicModesService:
    """Focused strategic prediction, blueprint design, audit, and revision."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient(task_type="strategic_modes")

    def predict_project(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        brief = self._required_text(payload, "brief")
        project_type = payload.get("project_type", "umum")
        depth = payload.get("depth", "seimbang")
        horizon = payload.get("horizon", "90 hari")
        constraints = payload.get("constraints", "")
        goals = payload.get("goals", "")

        system = """Kamu adalah analis strategi senior untuk project, bisnis, produk, dan keputusan eksekusi.
Tugasmu bukan memberi motivasi, tapi membuat prediksi operasional yang tajam, realistis, dan bisa dieksekusi.
Selalu bedakan fakta, asumsi, risiko, dan prediksi.
Balas hanya JSON valid tanpa markdown."""

        user = f"""Analisis project berikut.

Jenis project: {project_type}
Kedalaman analisis: {depth}
Horizon prediksi: {horizon}
Tujuan: {goals or '-'}
Constraint: {constraints or '-'}

Brief project:
{brief}

Return JSON dengan schema:
{{
  "mode": "project_prediction",
  "project_summary": "ringkasan 2-4 kalimat",
  "prediction": {{
    "likely_outcome": "prediksi outcome paling mungkin",
    "confidence": "low|medium|high",
    "confidence_reason": "alasan confidence",
    "time_horizon": "horizon yang dianalisis"
  }},
  "key_assumptions": ["..."],
  "success_drivers": ["..."],
  "critical_risks": [{{"risk": "...", "severity": "low|medium|high", "mitigation": "..."}}],
  "bottlenecks": ["..."],
  "scenarios": {{
    "best_case": "...",
    "base_case": "...",
    "worst_case": "..."
  }},
  "roadmap": {{
    "next_7_days": ["..."],
    "next_30_days": ["..."],
    "next_90_days": ["..."]
  }},
  "decision": {{
    "recommendation": "go|revise|pause|kill",
    "reason": "...",
    "next_action": "aksi paling penting berikutnya"
  }}
}}"""
        return self._chat_json(system, user, "prediction_project", temperature=0.25)

    def predict_question(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        question = self._required_text(payload, "question")
        context = payload.get("context", "")
        mode = payload.get("mode", "balanced")

        system = """Kamu adalah mesin prediksi keputusan. Jawab pertanyaan spesifik dengan ringkas, tajam, dan probabilistik.
Jangan melebar ke simulasi sosial penuh kecuali konteks memang meminta.
Balas hanya JSON valid tanpa markdown."""

        user = f"""Pertanyaan:
{question}

Konteks tambahan:
{context or '-'}

Mode jawaban: {mode}

Return JSON dengan schema:
{{
  "mode": "question_prediction",
  "direct_answer": "jawaban langsung",
  "prediction": "prediksi utama",
  "confidence": "low|medium|high",
  "confidence_reason": "...",
  "drivers": ["faktor utama yang mendorong prediksi"],
  "risks": ["risiko/variabel pengganggu"],
  "counter_arguments": ["argumen yang melemahkan prediksi"],
  "what_would_change_my_mind": ["data/kondisi yang akan mengubah kesimpulan"],
  "next_best_action": "aksi berikutnya yang paling masuk akal"
}}"""
        return self._chat_json(system, user, "prediction_question", temperature=0.2)

    def design_blueprint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        brief = self._required_text(payload, "brief")
        blueprint_type = payload.get("blueprint_type", "project")
        target_user = payload.get("target_user", "")
        constraints = payload.get("constraints", "")
        output_focus = payload.get("output_focus", [])

        system = """Kamu adalah arsitek blueprint senior untuk produk, bisnis, sistem, dan strategi eksekusi.
Buat rancangan yang jelas, modular, dan bisa diaudit. Jangan overengineering.
Balas hanya JSON valid tanpa markdown."""

        user = f"""Buat blueprint dari brief berikut.

Tipe blueprint: {blueprint_type}
Target user: {target_user or '-'}
Constraint: {constraints or '-'}
Fokus output: {json.dumps(output_focus, ensure_ascii=False)}

Brief:
{brief}

Return JSON dengan schema:
{{
  "mode": "blueprint_design",
  "title": "nama blueprint",
  "executive_summary": "ringkasan",
  "objectives": ["..."],
  "target_users": ["..."],
  "problem_statement": "...",
  "solution_concept": "...",
  "core_features": [{{"name": "...", "purpose": "...", "priority": "must|should|could"}}],
  "user_flow": ["langkah user dari awal sampai output"],
  "system_architecture": [{{"component": "...", "role": "...", "notes": "..."}}],
  "data_flow": ["..."],
  "ai_workflow": ["..."],
  "mvp_scope": ["..."],
  "roadmap": {{
    "phase_1": ["..."],
    "phase_2": ["..."],
    "phase_3": ["..."]
  }},
  "risks": [{{"risk": "...", "mitigation": "..."}}],
  "open_questions": ["..."],
  "next_steps": ["..."],
  "audit_offer": {{"recommended": true, "reason": "kenapa blueprint ini perlu diaudit"}}
}}"""
        return self._chat_json(system, user, "blueprint_design", temperature=0.25)

    def audit_blueprint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        blueprint = self._required_text(payload, "blueprint")
        audit_mode = payload.get("audit_mode", "balanced")
        context = payload.get("context", "")

        system = """Kamu adalah auditor blueprint dan red-team strategist.
Tugasmu menemukan kelemahan, asumsi palsu, risiko tersembunyi, dan bagian yang belum siap dieksekusi.
Tetap konstruktif: setiap kritik harus punya perbaikan.
Balas hanya JSON valid tanpa markdown."""

        user = f"""Audit blueprint berikut.

Mode audit: {audit_mode}
Konteks tambahan: {context or '-'}

Blueprint:
{blueprint}

Return JSON dengan schema:
{{
  "mode": "blueprint_audit",
  "score": 0,
  "verdict": "excellent|good|needs_revision|high_risk|not_ready",
  "summary": "ringkasan audit",
  "strengths": ["..."],
  "critical_weaknesses": [{{"issue": "...", "impact": "...", "fix": "..."}}],
  "hidden_assumptions": ["..."],
  "risk_register": [{{"risk": "...", "probability": "low|medium|high", "impact": "low|medium|high", "mitigation": "..."}}],
  "missing_parts": ["..."],
  "overengineered_parts": ["..."],
  "priority_fixes": ["..."],
  "recommendation": {{
    "action": "approve|revise|redesign|pause",
    "reason": "..."
  }},
  "revise_offer": {{"recommended": true, "reason": "kenapa revisi otomatis disarankan/tidak"}}
}}"""
        return self._chat_json(system, user, "blueprint_audit", temperature=0.2)

    def revise_blueprint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        blueprint = self._required_text(payload, "blueprint")
        audit = self._required_text(payload, "audit")
        revision_goal = payload.get("revision_goal", "perbaiki kelemahan kritis dan buat lebih executable")

        system = """Kamu adalah blueprint editor senior. Revisi rancangan berdasarkan audit.
Pertahankan bagian yang kuat, hapus overengineering, dan buat versi yang lebih siap dieksekusi.
Balas hanya JSON valid tanpa markdown."""

        user = f"""Revisi blueprint berikut berdasarkan audit.

Goal revisi: {revision_goal}

Blueprint awal:
{blueprint}

Audit:
{audit}

Return JSON dengan schema:
{{
  "mode": "blueprint_revision",
  "revision_summary": "apa yang berubah dan kenapa",
  "revised_blueprint": {{
    "title": "...",
    "executive_summary": "...",
    "objectives": ["..."],
    "core_features": [{{"name": "...", "purpose": "...", "priority": "must|should|could"}}],
    "architecture": [{{"component": "...", "role": "..."}}],
    "mvp_scope": ["..."],
    "roadmap": {{"phase_1": ["..."], "phase_2": ["..."], "phase_3": ["..."]}},
    "risk_controls": ["..."],
    "next_steps": ["..."]
  }},
  "changes_made": ["..."],
  "remaining_risks": ["..."],
  "audit_again_offer": {{"recommended": true, "reason": "..."}}
}}"""
        return self._chat_json(system, user, "blueprint_revision", temperature=0.25)

    def _chat_json(self, system: str, user: str, task_type: str, temperature: float) -> Dict[str, Any]:
        return self.llm.chat_json(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=4096,
            task_type=task_type,
        )

    @staticmethod
    def _required_text(payload: Dict[str, Any], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Field '{key}' wajib diisi")
        return value.strip()
