from __future__ import annotations

from typing import Any, Dict

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel

from ...config import get
from ..exceptions import ModelUnavailableError
from ..types import ModelSpec


def build_anthropic(model_name: str, spec: ModelSpec, **kwargs: Any) -> BaseChatModel:
    api_key = kwargs.pop("api_key", None) or get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ModelUnavailableError("ANTHROPIC_API_KEY is required for Claude models")

    temperature = kwargs.pop("temperature", 0.3)
    max_tokens = kwargs.pop("max_tokens", 4000)

    return ChatAnthropic(
        anthropic_api_key=api_key,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
