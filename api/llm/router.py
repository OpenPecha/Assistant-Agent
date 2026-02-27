from __future__ import annotations

import json
from typing import Any, Dict, Optional

from langchain_core.language_models import BaseChatModel

from ..config import get
from .exceptions import ModelUnavailableError, UnsupportedModelError
from .registry import REGISTRY, resolve_model_name
from .types import ModelSpec


def _stable_cache_key(model_name: str, kwargs: Dict[str, Any]) -> str:
    return f"{model_name}:{json.dumps(kwargs, sort_keys=True, default=str)}"


class ModelRouter:

    def __init__(self) -> None:
        self._cache: Dict[str, BaseChatModel] = {}

    def get_spec(self, model_name: str) -> ModelSpec:
        key = resolve_model_name(model_name)
        spec = REGISTRY.get(key)
        if not spec:
            raise UnsupportedModelError(f"Unsupported model: {model_name}")
        return spec

    def validate_model_availability(self, model_name: str) -> bool:
        try:
            spec = self.get_spec(model_name)
        except UnsupportedModelError:
            return False
        return self._has_credential(spec)

    def available_models(self) -> Dict[str, Dict[str, Any]]:
        out: Dict[str, Dict[str, Any]] = {}
        for name, spec in REGISTRY.items():
            if self._has_credential(spec):
                out[name] = {
                    "name": spec.display_name,
                    "provider": spec.provider,
                    "description": spec.description,
                    "is_thinking": spec.is_thinking,
                    "capabilities": list(spec.capabilities),
                    "context_window": spec.context_window,
                }
        return out

    def get_model(self, model_name: str, **kwargs: Any) -> BaseChatModel:
        spec = self.get_spec(model_name)
        if not self._has_credential(spec, kwargs=kwargs):
            raise ModelUnavailableError(
                f"Model '{spec.name}' is configured but unavailable (missing credential: {spec.required_credential})."
            )

        if "api_key" in kwargs and kwargs["api_key"]:
            return spec.build(model_name=spec.name, spec=spec, **kwargs)

        cache_key = _stable_cache_key(spec.name, kwargs)
        if cache_key not in self._cache:
            self._cache[cache_key] = spec.build(model_name=spec.name, spec=spec, **kwargs)
        return self._cache[cache_key]

    def _has_credential(self, spec: ModelSpec, kwargs: Optional[Dict[str, Any]] = None) -> bool:
        kwargs = kwargs or {}
        if kwargs.get("api_key"):
            return True
        if not spec.required_credential:
            return True
        return bool(get(spec.required_credential))


_model_router = ModelRouter()

def get_model_router() -> ModelRouter:
    return _model_router
