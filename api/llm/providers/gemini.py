from __future__ import annotations

from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel

from ...config import get
from ..exceptions import ModelUnavailableError
from ..types import ModelSpec
from ..wrappers.gemini_wrapper import GeminiModelWrapper


def build_gemini(model_name: str, spec: ModelSpec, **kwargs: Any) -> BaseChatModel:

    api_key = kwargs.pop("api_key", None) or get("GEMINI_API_KEY")
    if not api_key:
        raise ModelUnavailableError("GEMINI_API_KEY is required for Gemini models")

    temperature = kwargs.pop("temperature", 0.3)
    max_tokens = kwargs.pop("max_tokens", 16000)

    user_gc = kwargs.get("generation_config") or {}
    max_out = user_gc.get("max_output_tokens", max_tokens)

    provider_model_name = spec.provider_model_name or model_name

    base = ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model=provider_model_name,
        temperature=temperature,
        max_output_tokens=max_out,
        **{k: v for k, v in kwargs.items() if k not in ["generation_config"]},
    )

    base_gc: Dict[str, Any] = {
        "response_mime_type": "application/json",
        "max_output_tokens": max_out,
        **user_gc,
    }

    if model_name == "gemini-2.5-flash":
        thinking_gc = {"thinking_config": {"thinking_budget": 0}}
    elif model_name == "gemini-2.5-flash-thinking":
        thinking_gc = {"thinking_config": {"thinking_budget": 12000}}
    else:
        thinking_gc = {"thinking_config": {"thinking_budget": 12000}}

    default_gc = {**base_gc, **thinking_gc}

    return GeminiModelWrapper(base, default_generation_config=default_gc)
