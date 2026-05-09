"""AI provider/model settings API."""

from flask import jsonify, request
from openai import OpenAI

from . import ai_bp
from ..services.ai_provider_store import AIProviderStore
from ..utils.logger import get_logger

logger = get_logger('mirofish.ai_api')


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


@ai_bp.route('/providers', methods=['GET'])
def list_providers():
    providers = AIProviderStore.list()
    active = AIProviderStore.resolve_active_or_env()
    active_public = dict(active)
    if active_public.get('api_key'):
        active_public['api_key_masked'] = AIProviderStore._mask_secret(active_public.get('api_key'))
        active_public.pop('api_key', None)
    return _ok({"providers": providers, "active": active_public})


@ai_bp.route('/providers', methods=['POST'])
def upsert_provider():
    try:
        payload = _json_payload()
        provider = AIProviderStore.upsert(payload)
        return _ok(provider)
    except ValueError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        logger.exception("Upsert AI provider failed")
        return _error(str(exc), 500)


@ai_bp.route('/providers/<provider_id>', methods=['GET'])
def get_provider(provider_id):
    provider = AIProviderStore.get(provider_id)
    if not provider:
        return _error("provider_id tidak ditemukan", 404)
    return _ok(provider)


@ai_bp.route('/providers/<provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    deleted = AIProviderStore.delete(provider_id)
    if not deleted:
        return _error("provider_id tidak ditemukan", 404)
    return _ok({"deleted": True, "provider_id": provider_id})


@ai_bp.route('/providers/<provider_id>/activate', methods=['POST'])
def activate_provider(provider_id):
    provider = AIProviderStore.set_active(provider_id)
    if not provider:
        return _error("provider_id tidak ditemukan", 404)
    return _ok(provider)


@ai_bp.route('/active', methods=['GET'])
def get_active_provider():
    active = AIProviderStore.resolve_active_or_env()
    if active.get('api_key'):
        active['api_key_masked'] = AIProviderStore._mask_secret(active.get('api_key'))
        active.pop('api_key', None)
    return _ok(active)


@ai_bp.route('/test', methods=['POST'])
def test_provider():
    """Test a provider config or saved provider_id with a tiny chat call."""
    try:
        payload = _json_payload()
        if payload.get('provider_id'):
            provider = AIProviderStore.get(payload['provider_id'], include_secrets=True)
            if not provider:
                return _error("provider_id tidak ditemukan", 404)
        else:
            provider = {
                "base_url": AIProviderStore._normalize_base_url(str(payload.get('base_url') or '')),
                "api_key": payload.get('api_key'),
                "default_model": payload.get('default_model') or payload.get('model'),
            }
        if not provider.get('base_url') or not provider.get('api_key') or not provider.get('default_model'):
            raise ValueError("base_url, api_key, dan default_model wajib diisi untuk test")

        client = OpenAI(api_key=provider['api_key'], base_url=provider['base_url'])
        response = client.chat.completions.create(
            model=provider['default_model'],
            messages=[{"role": "user", "content": "Reply exactly: OK"}],
            temperature=0.1,
            max_tokens=int(payload.get('max_tokens') or 128),
        )
        content = response.choices[0].message.content or ""
        usage = getattr(response, 'usage', None)
        usage_data = usage.model_dump() if hasattr(usage, 'model_dump') else None
        return _ok({
            "ok": True,
            "provider_id": provider.get('provider_id'),
            "base_url": provider.get('base_url'),
            "model": provider.get('default_model'),
            "response": content,
            "usage": usage_data,
        })
    except ValueError as exc:
        return _error(str(exc), 400)
    except Exception as exc:
        logger.exception("AI provider test failed")
        return _error(str(exc), 500)


@ai_bp.route('/models', methods=['GET'])
def list_models():
    """Return model list for active or selected provider.

    For OpenAI-compatible providers, tries /v1/models. If unavailable, falls back
    to locally saved models/default_model.
    """
    provider_id = request.args.get('provider_id')
    include_remote = request.args.get('remote', default='true').lower() in {'1', 'true', 'yes', 'on'}
    provider = AIProviderStore.get(provider_id, include_secrets=True) if provider_id else AIProviderStore.resolve_active_or_env()
    if not provider:
        return _error("provider_id tidak ditemukan", 404)

    local_models = provider.get('models') or []
    remote_models = []
    remote_error = None
    if include_remote and provider.get('api_key') and provider.get('base_url'):
        try:
            client = OpenAI(api_key=provider['api_key'], base_url=provider['base_url'])
            models = client.models.list()
            for model in getattr(models, 'data', []) or []:
                model_id = getattr(model, 'id', None)
                if model_id:
                    remote_models.append(model_id)
        except Exception as exc:
            remote_error = str(exc)[:500]

    merged = []
    for model in remote_models + local_models + [provider.get('default_model')]:
        if model and model not in merged:
            merged.append(model)
    return _ok({
        "provider_id": provider.get('provider_id'),
        "active": bool(provider.get('is_active')),
        "models": merged,
        "remote_models": remote_models,
        "local_models": local_models,
        "remote_error": remote_error,
    })
