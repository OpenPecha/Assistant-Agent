from __future__ import annotations

from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from ..exceptions import ModelUnavailableError
from ..types import ModelSpec


def build_openai(settings: Any, model_name: str, spec: ModelSpec, **kwargs: Any) -> BaseChatModel:
    api_key = kwargs.pop("api_key", None) or getattr(settings, "openai_api_key", None)
    if not api_key:
        raise ModelUnavailableError("OPENAI_API_KEY is required for OpenAI models")

    temperature = kwargs.pop("temperature", 0.3)
    max_tokens = kwargs.pop("max_tokens", 4000)

    return ChatOpenAI(
        openai_api_key=api_key,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
