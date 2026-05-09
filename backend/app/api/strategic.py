"""API endpoints for focused strategic modes."""

from flask import jsonify, request

from . import strategic_bp
from ..services.strategic_modes import StrategicModesService
from ..utils.logger import get_logger

logger = get_logger('mirofish.strategic_api')


def _json_payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Request body harus JSON object")
    return data


def _ok(data):
    return jsonify({"success": True, "data": data})


def _error(message, status=400):
    return jsonify({"success": False, "error": message}), status


@strategic_bp.route('/prediction/project', methods=['POST'])
def predict_project():
    """Focused project/business/product prediction."""
    try:
        payload = _json_payload()
        result = StrategicModesService().predict_project(payload)
        return _ok(result)
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
        result = StrategicModesService().predict_question(payload)
        return _ok(result)
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
        result = StrategicModesService().design_blueprint(payload)
        return _ok(result)
    except ValueError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        logger.exception("Blueprint design failed")
        return _error(str(exc), 500)


@strategic_bp.route('/blueprint/audit', methods=['POST'])
def audit_blueprint():
    """Audit an existing blueprint."""
    try:
        payload = _json_payload()
        result = StrategicModesService().audit_blueprint(payload)
        return _ok(result)
    except ValueError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        logger.exception("Blueprint audit failed")
        return _error(str(exc), 500)


@strategic_bp.route('/blueprint/revise', methods=['POST'])
def revise_blueprint():
    """Revise a blueprint based on an audit."""
    try:
        payload = _json_payload()
        result = StrategicModesService().revise_blueprint(payload)
        return _ok(result)
    except ValueError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        logger.exception("Blueprint revision failed")
        return _error(str(exc), 500)
