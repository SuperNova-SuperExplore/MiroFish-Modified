"""Native Blueprint Lab engine.

Runs focused blueprint evaluation rounds without the OASIS social subprocess.
It keeps the same high-level MiroFish flow, but Step 3 can use these native
review events instead of Twitter/Reddit actions.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..config import Config
from ..models.project import ProjectManager
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger

logger = get_logger('mirofish.blueprint_engine')

BLUEPRINT_RUNS_DIR = os.path.join(Config.UPLOAD_FOLDER, 'blueprint_runs')

CORE_EVALUATORS = [
    {"id": "product_architect", "name": "Product Architect", "lens": "produk, value proposition, MVP scope, prioritas fitur"},
    {"id": "technical_architect", "name": "Technical Architect", "lens": "arsitektur, integrasi, data flow, feasibility teknis"},
    {"id": "risk_auditor", "name": "Risk Auditor", "lens": "risiko kritis, blocker, mitigasi, severity"},
    {"id": "ux_reviewer", "name": "UX Reviewer", "lens": "alur user, friksi, onboarding, usability"},
    {"id": "business_strategist", "name": "Business Strategist", "lens": "market, positioning, monetisasi, go-to-market"},
    {"id": "finance_controller", "name": "Finance Controller", "lens": "biaya, resource, prioritas budget, risiko finansial"},
    {"id": "execution_planner", "name": "Execution Planner", "lens": "roadmap, milestone, dependency, next action"},
    {"id": "red_team_critic", "name": "Red-Team Critic", "lens": "blind spot, asumsi rapuh, overengineering, counterpoint"},
    {"id": "target_user_rep", "name": "Target User Representative", "lens": "pain point user, validasi kebutuhan, manfaat nyata"},
]

ROUND_PLAN = [
    {"round": 1, "name": "Blueprint Understanding", "focus": "pahami tujuan, user, modul, scope, dan pertanyaan terbuka", "type": "INSIGHT"},
    {"round": 2, "name": "Risk & Assumption Audit", "focus": "temukan risiko, asumsi lemah, blocker, dan mitigasi", "type": "RISK_FLAG"},
    {"round": 3, "name": "Feasibility Review", "focus": "uji teknis, bisnis, UX, biaya, dan dependency", "type": "CRITIQUE"},
    {"round": 4, "name": "MVP & Revision Planning", "focus": "tentukan must-have, cut-list, roadmap, dan prioritas revisi", "type": "REVISION_NOTE"},
    {"round": 5, "name": "Final Verdict", "focus": "beri readiness score, verdict, dan next 7/30/90 days", "type": "SCORE_UPDATE"},
]


def _now() -> str:
    return datetime.now().isoformat()


class BlueprintLabEngine:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient(task_type="blueprint_engine")
        os.makedirs(BLUEPRINT_RUNS_DIR, exist_ok=True)

    def _run_dir(self, run_id: str) -> str:
        path = os.path.join(BLUEPRINT_RUNS_DIR, run_id)
        os.makedirs(path, exist_ok=True)
        return path

    def _path(self, run_id: str, filename: str) -> str:
        return os.path.join(self._run_dir(run_id), filename)

    def _save_json(self, run_id: str, filename: str, data: Any):
        with open(self._path(run_id, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_json(self, run_id: str, filename: str, default: Any = None) -> Any:
        path = self._path(run_id, filename)
        if not os.path.exists(path):
            return default
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def start_run(self, simulation_id: str, project_id: str, graph_id: str, simulation_requirement: str) -> Dict[str, Any]:
        run_id = f"bpr_{uuid.uuid4().hex[:12]}"
        document_text = ProjectManager.get_extracted_text(project_id) or ""
        state = {
            "run_id": run_id,
            "simulation_id": simulation_id,
            "project_id": project_id,
            "graph_id": graph_id,
            "status": "running",
            "current_round": 0,
            "total_rounds": len(ROUND_PLAN),
            "created_at": _now(),
            "updated_at": _now(),
            "operation_mode": "blueprint_lab",
        }
        self._save_json(run_id, 'state.json', state)
        self._save_json(run_id, 'events.json', [])

        try:
            result = self._run_all_rounds(run_id, simulation_requirement, document_text)
            state.update({
                "status": "completed",
                "current_round": len(ROUND_PLAN),
                "completed_at": _now(),
                "updated_at": _now(),
                "artifacts": result.get("artifacts", {}),
            })
            self._save_json(run_id, 'state.json', state)
        except Exception as exc:
            logger.error(f"Blueprint engine gagal: {exc}")
            state.update({"status": "failed", "error": str(exc), "updated_at": _now()})
            self._save_json(run_id, 'state.json', state)
            raise

        return self.get_run(run_id)

    def _run_all_rounds(self, run_id: str, simulation_requirement: str, document_text: str) -> Dict[str, Any]:
        events: List[Dict[str, Any]] = []
        round_outputs: List[Dict[str, Any]] = []
        blueprint_context = document_text[:18000]

        for round_info in ROUND_PLAN:
            state = self._load_json(run_id, 'state.json', {})
            state.update({"current_round": round_info["round"], "updated_at": _now()})
            self._save_json(run_id, 'state.json', state)

            output = self._run_round(round_info, simulation_requirement, blueprint_context, round_outputs)
            round_outputs.append(output)
            for item in output.get('events', []):
                events.append(self._normalize_event(run_id, round_info, item, len(events)))
            self._save_json(run_id, 'events.json', events)

        artifacts = self._synthesize_artifacts(simulation_requirement, blueprint_context, round_outputs, events)
        self._save_json(run_id, 'round_outputs.json', round_outputs)
        self._save_json(run_id, 'artifacts.json', artifacts)
        with open(self._path(run_id, 'blueprint_report.md'), 'w', encoding='utf-8') as f:
            f.write(artifacts.get('blueprint_report_md', ''))
        with open(self._path(run_id, 'blueprint_v2.md'), 'w', encoding='utf-8') as f:
            f.write(artifacts.get('blueprint_v2_md', ''))
        return {"artifacts": artifacts}

    def _run_round(self, round_info: Dict[str, Any], requirement: str, blueprint: str, previous: List[Dict[str, Any]]) -> Dict[str, Any]:
        system = """Kamu adalah Blueprint Lab Engine. Jalankan audit blueprint native, bukan simulasi sosial.
Balas JSON valid. Bahasa Indonesia. Buat event tajam, actionable, dan berbasis evaluator panel."""
        user = f"""Round: {round_info['round']} - {round_info['name']}
Focus: {round_info['focus']}
Default event type: {round_info['type']}

Evaluator panel:
{json.dumps(CORE_EVALUATORS, ensure_ascii=False, indent=2)}

Requirement:
{requirement}

Blueprint/context:
{blueprint}

Previous rounds:
{json.dumps(previous, ensure_ascii=False)[:8000]}

Return JSON:
{{
  "round": {round_info['round']},
  "name": "{round_info['name']}",
  "events": [
    {{
      "agent_id": "risk_auditor",
      "agent_name": "Risk Auditor",
      "type": "{round_info['type']}",
      "target": "fitur/modul/asumsi/dependency",
      "severity": "low|medium|high|critical",
      "content": "temuan evaluator",
      "recommendation": "aksi revisi konkret"
    }}
  ],
  "summary": "ringkasan round",
  "score_delta": -10
}}
Buat 6-10 events. Pastikan ada minimal satu risk/assumption/dependency/revision insight bila relevan."""
        return self.llm.chat_json(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.25,
        )

    def _normalize_event(self, run_id: str, round_info: Dict[str, Any], item: Dict[str, Any], idx: int) -> Dict[str, Any]:
        event_type = item.get('type') or round_info.get('type') or 'INSIGHT'
        agent_id = item.get('agent_id') or 'blueprint_engine'
        agent_name = item.get('agent_name') or agent_id.replace('_', ' ').title()
        return {
            "id": f"{run_id}_evt_{idx:04d}",
            "run_id": run_id,
            "round": round_info.get('round'),
            "round_name": round_info.get('name'),
            "platform": "blueprint",
            "action_type": event_type,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "timestamp": _now(),
            "target": item.get('target', ''),
            "severity": item.get('severity', 'medium'),
            "action_args": {
                "content": item.get('content', ''),
                "recommendation": item.get('recommendation', ''),
                "target": item.get('target', ''),
                "severity": item.get('severity', 'medium'),
            },
        }

    def _synthesize_artifacts(self, requirement: str, blueprint: str, rounds: List[Dict[str, Any]], events: List[Dict[str, Any]]) -> Dict[str, Any]:
        system = """Kamu adalah Blueprint Lab synthesis engine. Buat artifact final yang actionable.
Balas JSON valid. Bahasa Indonesia."""
        user = f"""Requirement:
{requirement}

Blueprint/context:
{blueprint[:14000]}

Round outputs:
{json.dumps(rounds, ensure_ascii=False)[:18000]}

Events:
{json.dumps(events, ensure_ascii=False)[:16000]}

Return JSON:
{{
  "readiness_score": 0,
  "verdict": "go|revise|pause|kill",
  "executive_summary": "...",
  "critical_risks": [{{"risk":"...","severity":"high","mitigation":"..."}}],
  "hidden_assumptions": [{{"assumption":"...","validation":"..."}}],
  "dependency_map": [{{"dependency":"...","blocks":"...","owner":"..."}}],
  "mvp_scope": {{"must_have":["..."],"cut_or_later":["..."],"why":"..."}},
  "revision_priorities": [{{"priority":"P0|P1|P2","change":"...","reason":"..."}}],
  "next_7_30_90_days": {{"next_7_days":["..."],"next_30_days":["..."],"next_90_days":["..."]}},
  "blueprint_report_md": "Markdown laporan audit lengkap",
  "blueprint_v2_md": "Markdown blueprint revisi v2"
}}"""
        return self.llm.chat_json(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.2,
        )

    def get_run(self, run_id: str) -> Dict[str, Any]:
        state = self._load_json(run_id, 'state.json', {})
        if not state:
            raise ValueError(f"Blueprint run tidak ditemukan: {run_id}")
        events = self._load_json(run_id, 'events.json', [])
        artifacts = self._load_json(run_id, 'artifacts.json', {})
        return {"state": state, "events": events, "artifacts": artifacts}

    def find_by_simulation(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(BLUEPRINT_RUNS_DIR):
            return None
        for run_id in sorted(os.listdir(BLUEPRINT_RUNS_DIR), reverse=True):
            state = self._load_json(run_id, 'state.json', {})
            if state.get('simulation_id') == simulation_id:
                return self.get_run(run_id)
        return None
