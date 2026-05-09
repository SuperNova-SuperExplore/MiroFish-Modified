"""Blueprint Lab native engine API."""

from flask import jsonify, request

from . import blueprint_bp
from ..models.project import ProjectManager
from ..services.blueprint_engine import BlueprintLabEngine
from ..services.simulation_manager import SimulationManager
from ..utils.logger import get_logger

logger = get_logger('mirofish.blueprint_api')


def _ok(data=None, **extra):
    body = {"success": True}
    if data is not None:
        body["data"] = data
    body.update(extra)
    return jsonify(body)


def _error(message, status=400):
    return jsonify({"success": False, "error": message}), status


@blueprint_bp.route('/runs', methods=['POST'])
def start_blueprint_run():
    try:
        data = request.get_json(silent=True) or {}
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return _error('simulation_id wajib diisi')

        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        if not state:
            return _error(f'simulasi tidak ditemukan: {simulation_id}', 404)

        project = ProjectManager.get_project(state.project_id)
        if not project:
            return _error(f'project tidak ditemukan: {state.project_id}', 404)

        mode = getattr(project, 'operation_mode', None) or getattr(state, 'operation_mode', None)
        requirement = getattr(project, 'simulation_requirement', '') or ''
        if mode != 'blueprint_lab' and 'Mode: Blueprint Lab' not in requirement:
            return _error('Blueprint engine hanya untuk operation_mode blueprint_lab')

        engine = BlueprintLabEngine()
        existing = engine.find_by_simulation(simulation_id)
        if existing and not data.get('force'):
            return _ok(existing, already_exists=True)

        run = engine.start_run(
            simulation_id=simulation_id,
            project_id=state.project_id,
            graph_id=state.graph_id,
            simulation_requirement=project.simulation_requirement or '',
        )
        return _ok(run)
    except Exception as exc:
        logger.error(f'gagal menjalankan Blueprint engine: {exc}')
        return _error(str(exc), 500)


@blueprint_bp.route('/runs/by-simulation/<simulation_id>', methods=['GET'])
def get_blueprint_run_by_simulation(simulation_id):
    try:
        run = BlueprintLabEngine().find_by_simulation(simulation_id)
        if not run:
            return _error('blueprint run belum ada', 404)
        return _ok(run)
    except Exception as exc:
        return _error(str(exc), 500)


@blueprint_bp.route('/runs/<run_id>', methods=['GET'])
def get_blueprint_run(run_id):
    try:
        return _ok(BlueprintLabEngine().get_run(run_id))
    except Exception as exc:
        return _error(str(exc), 404)


@blueprint_bp.route('/runs/<run_id>/events', methods=['GET'])
def get_blueprint_events(run_id):
    try:
        run = BlueprintLabEngine().get_run(run_id)
        return _ok(run.get('events', []))
    except Exception as exc:
        return _error(str(exc), 404)


@blueprint_bp.route('/runs/<run_id>/artifacts', methods=['GET'])
def get_blueprint_artifacts(run_id):
    try:
        run = BlueprintLabEngine().get_run(run_id)
        return _ok(run.get('artifacts', {}))
    except Exception as exc:
        return _error(str(exc), 404)
