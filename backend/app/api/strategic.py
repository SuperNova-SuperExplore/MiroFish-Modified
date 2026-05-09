"""API endpoints for focused strategic modes."""

import json

from flask import jsonify, request

from . import strategic_bp
from ..services.strategic_modes import StrategicModesService
from ..services.strategic_store import StrategicOperationStore, title_from_output
from ..utils.logger import get_logger

logger = get_logger('mirofish.strategic_api')


def _json_payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Request body harus JSON object")
    return data


def _ok(data=None, **extra):
    body = {"success": True}
    if data is not None:
        body["data"] = data
    body.update(extra)
    return jsonify(body)


def _error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def _operation_response(operation):
    return _ok(
        operation.get("output"),
        operation_id=operation.get("operation_id"),
        parent_operation_id=operation.get("parent_operation_id"),
        operation=operation,
    )


def _save_operation(mode, payload, result, service, parent_operation_id=None):
    operation = StrategicOperationStore.create(
        mode=mode,
        input_data=payload,
        output_data=result,
        title=title_from_output(mode, result, fallback=mode.replace("_", " ").title()),
        parent_operation_id=parent_operation_id,
        model=getattr(service.llm, "model", None),
        provider_base_url=getattr(service.llm, "base_url", None),
    )
    return operation


def _operation_text(operation, key="output"):
    value = operation.get(key)
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2)


@strategic_bp.route('/modes', methods=['GET'])
def get_modes():
    """Return mode metadata for frontend mode selector and forms."""
    modes = [
        {
            "id": "full_predict",
            "name": "Full Predict",
            "label": "Prediksi Penuh",
            "category": "simulation",
            "status": "existing_pipeline",
            "endpoint": "/api/simulation",
            "cta": "Jalankan Simulasi Penuh",
            "badges": ["Dalam", "Multi-agent", "Sosial"],
            "best_for": [
                "Isu sosial luas dengan banyak aktor",
                "Prediksi reaksi publik atau komunitas",
                "Simulasi konflik, dukungan, backlash, dan narasi dominan",
            ],
            "not_for": [
                "Pertanyaan cepat",
                "Audit rancangan internal",
                "Project planning sederhana",
            ],
            "description": "Mode lengkap MiroFish: graph, agent profile, simulasi OASIS, interview, dan laporan prediksi.",
            "input_fields": [
                {"name": "topic_or_document", "type": "text_or_file", "required": True, "label": "Topik atau dokumen"},
                {"name": "simulation_requirement", "type": "textarea", "required": True, "label": "Kebutuhan simulasi"},
                {"name": "platforms", "type": "multi_select", "options": ["twitter", "reddit"], "default": ["twitter", "reddit"]},
            ],
        },
        {
            "id": "project_prediction",
            "name": "Prediksi Project",
            "category": "focused_prediction",
            "status": "ready",
            "endpoint": "/api/strategic/prediction/project",
            "cta": "Analisis Project",
            "badges": ["Fokus", "Strategis", "Roadmap"],
            "best_for": [
                "Menilai project, bisnis, produk, atau keputusan besar",
                "Mencari risiko, bottleneck, dan peluang sukses",
                "Membuat roadmap 7/30/90 hari",
            ],
            "description": "Prediksi terarah untuk project tanpa menjalankan simulasi sosial penuh.",
            "input_fields": [
                {"name": "brief", "type": "textarea", "required": True, "label": "Brief project"},
                {"name": "project_type", "type": "select", "required": False, "label": "Jenis project", "options": ["software", "bisnis", "produk", "konten", "operasional", "umum"], "default": "umum"},
                {"name": "depth", "type": "select", "required": False, "label": "Kedalaman", "options": ["quick", "seimbang", "dalam", "brutal"], "default": "seimbang"},
                {"name": "horizon", "type": "text", "required": False, "label": "Horizon prediksi", "default": "90 hari"},
                {"name": "goals", "type": "textarea", "required": False, "label": "Tujuan"},
                {"name": "constraints", "type": "textarea", "required": False, "label": "Constraint"},
            ],
        },
        {
            "id": "question_prediction",
            "name": "Prediksi Pertanyaan",
            "category": "focused_prediction",
            "status": "ready",
            "endpoint": "/api/strategic/prediction/question",
            "cta": "Tanya Prediksi",
            "badges": ["Cepat", "Ringkas", "Decision Support"],
            "best_for": [
                "Satu pertanyaan spesifik",
                "Membandingkan pilihan",
                "Mencari next best action cepat",
            ],
            "description": "Jawaban prediktif cepat dengan confidence, risiko, counterargument, dan next action.",
            "input_fields": [
                {"name": "question", "type": "textarea", "required": True, "label": "Pertanyaan"},
                {"name": "context", "type": "textarea", "required": False, "label": "Konteks tambahan"},
                {"name": "mode", "type": "select", "required": False, "label": "Mode", "options": ["quick", "balanced", "counterargument", "scenario"], "default": "balanced"},
            ],
        },
        {
            "id": "blueprint_lab",
            "name": "Blueprint Lab",
            "category": "blueprint",
            "status": "ready",
            "cta": "Masuk Blueprint Lab",
            "badges": ["Rancang", "Audit", "Revisi"],
            "best_for": [
                "Merancang project, produk, sistem, bisnis, atau roadmap dari nol",
                "Mengaudit blueprint yang sudah ada",
                "Merevisi rancangan berdasarkan kritik",
            ],
            "description": "Lab untuk rancang → audit → revisi → audit ulang.",
            "sub_modes": [
                {
                    "id": "blueprint_design",
                    "name": "Rancang Blueprint",
                    "endpoint": "/api/strategic/blueprint/design",
                    "cta": "Buat Blueprint",
                    "next_offer": "audit",
                    "input_fields": [
                        {"name": "brief", "type": "textarea", "required": True, "label": "Brief rancangan"},
                        {"name": "blueprint_type", "type": "select", "required": False, "label": "Tipe blueprint", "options": ["project", "produk", "bisnis", "sistem", "software", "strategi"], "default": "project"},
                        {"name": "target_user", "type": "text", "required": False, "label": "Target user"},
                        {"name": "constraints", "type": "textarea", "required": False, "label": "Constraint"},
                        {"name": "output_focus", "type": "multi_select", "required": False, "label": "Fokus output", "options": ["roadmap", "architecture", "business_model", "risk", "mvp", "user_flow"]},
                    ],
                },
                {
                    "id": "blueprint_audit",
                    "name": "Audit Blueprint",
                    "endpoint": "/api/strategic/blueprint/audit",
                    "cta": "Audit Blueprint",
                    "next_offer": "revise",
                    "input_fields": [
                        {"name": "blueprint", "type": "textarea", "required": False, "label": "Blueprint mentah"},
                        {"name": "blueprint_operation_id", "type": "operation_ref", "required": False, "label": "Ambil dari blueprint tersimpan"},
                        {"name": "audit_mode", "type": "select", "required": False, "label": "Mode audit", "options": ["quick", "balanced", "technical", "business", "risk", "brutal", "investor", "ux"], "default": "balanced"},
                        {"name": "context", "type": "textarea", "required": False, "label": "Konteks tambahan"},
                    ],
                },
                {
                    "id": "blueprint_revision",
                    "name": "Revisi Blueprint",
                    "endpoint": "/api/strategic/blueprint/revise",
                    "cta": "Revisi Blueprint",
                    "next_offer": "audit_again",
                    "input_fields": [
                        {"name": "blueprint", "type": "textarea", "required": False, "label": "Blueprint mentah"},
                        {"name": "audit", "type": "textarea", "required": False, "label": "Audit mentah"},
                        {"name": "blueprint_operation_id", "type": "operation_ref", "required": False, "label": "Blueprint tersimpan"},
                        {"name": "audit_operation_id", "type": "operation_ref", "required": False, "label": "Audit tersimpan"},
                        {"name": "revision_goal", "type": "textarea", "required": False, "label": "Tujuan revisi", "default": "perbaiki kelemahan kritis dan buat lebih executable"},
                    ],
                },
            ],
        },
    ]
    return _ok(modes, count=len(modes))


@strategic_bp.route('/prediction/project', methods=['POST'])
def predict_project():
    """Focused project/business/product prediction."""
    try:
        payload = _json_payload()
        service = StrategicModesService()
        result = service.predict_project(payload)
        operation = _save_operation("project_prediction", payload, result, service)
        return _operation_response(operation)
    except ValueError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        logger.exception("Project prediction failed")
        return _error(str(exc), 500)


@strategic_bp.route('/prediction/question', methods=['POST'])
def predict_question():
    """Focused predictive answer for a specific question."""
    try:
        payload = _json_payload()
        service = StrategicModesService()
        result = service.predict_question(payload)
        operation = _save_operation("question_prediction", payload, result, service)
        return _operation_response(operation)
    except ValueError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        logger.exception("Question prediction failed")
        return _error(str(exc), 500)


@strategic_bp.route('/blueprint/design', methods=['POST'])
def design_blueprint():
    """Create a blueprint from a brief."""
    try:
        payload = _json_payload()
        service = StrategicModesService()
        result = service.design_blueprint(payload)
        operation = _save_operation("blueprint_design", payload, result, service)
        return _operation_response(operation)
    except ValueError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        logger.exception("Blueprint design failed")
        return _error(str(exc), 500)


@strategic_bp.route('/blueprint/audit', methods=['POST'])
def audit_blueprint():
    """Audit an existing blueprint or a saved blueprint operation."""
    try:
        payload = _json_payload()
        parent_operation_id = payload.get("blueprint_operation_id")
        if parent_operation_id and not payload.get("blueprint"):
            parent = StrategicOperationStore.get(parent_operation_id)
            if not parent:
                raise ValueError("blueprint_operation_id tidak ditemukan")
            payload = dict(payload)
            payload["blueprint"] = _operation_text(parent)

        service = StrategicModesService()
        result = service.audit_blueprint(payload)
        operation = _save_operation("blueprint_audit", payload, result, service, parent_operation_id)
        return _operation_response(operation)
    except ValueError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        logger.exception("Blueprint audit failed")
        return _error(str(exc), 500)


@strategic_bp.route('/blueprint/revise', methods=['POST'])
def revise_blueprint():
    """Revise a blueprint from raw text or saved blueprint/audit operations."""
    try:
        payload = _json_payload()
        parent_operation_id = payload.get("audit_operation_id") or payload.get("blueprint_operation_id")

        if payload.get("blueprint_operation_id") and not payload.get("blueprint"):
            blueprint_op = StrategicOperationStore.get(payload["blueprint_operation_id"])
            if not blueprint_op:
                raise ValueError("blueprint_operation_id tidak ditemukan")
            payload = dict(payload)
            payload["blueprint"] = _operation_text(blueprint_op)

        if payload.get("audit_operation_id") and not payload.get("audit"):
            audit_op = StrategicOperationStore.get(payload["audit_operation_id"])
            if not audit_op:
                raise ValueError("audit_operation_id tidak ditemukan")
            payload = dict(payload)
            payload["audit"] = _operation_text(audit_op)

        service = StrategicModesService()
        result = service.revise_blueprint(payload)
        operation = _save_operation("blueprint_revision", payload, result, service, parent_operation_id)
        return _operation_response(operation)
    except ValueError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        logger.exception("Blueprint revision failed")
        return _error(str(exc), 500)


@strategic_bp.route('/operations', methods=['GET'])
def list_operations():
    """List saved strategic operations."""
    try:
        limit = min(request.args.get('limit', default=50, type=int), 200)
        offset = max(request.args.get('offset', default=0, type=int), 0)
        mode = request.args.get('mode')
        parent_operation_id = request.args.get('parent_operation_id')
        operations = StrategicOperationStore.list(
            mode=mode,
            parent_operation_id=parent_operation_id,
            limit=limit,
            offset=offset,
        )
        return _ok(operations, count=len(operations))
    except Exception as exc:
        logger.exception("List strategic operations failed")
        return _error(str(exc), 500)


@strategic_bp.route('/operations/<operation_id>', methods=['GET'])
def get_operation(operation_id):
    """Get one saved strategic operation with children."""
    operation = StrategicOperationStore.get(operation_id)
    if not operation:
        return _error("operation_id tidak ditemukan", 404)
    operation["children"] = StrategicOperationStore.children(operation_id)
    return _ok(operation)


@strategic_bp.route('/operations/<operation_id>', methods=['DELETE'])
def delete_operation(operation_id):
    """Delete one saved strategic operation."""
    deleted = StrategicOperationStore.delete(operation_id)
    if not deleted:
        return _error("operation_id tidak ditemukan", 404)
    return _ok({"deleted": True, "operation_id": operation_id})
