from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel

from ..exceptions import ModelUnavailableError
from ..types import ModelSpec
from ..wrappers.dharmamitra_wrapper import DharmamitraModelWrapper


def build_dharmamitra(settings: Any, model_name: str, spec: ModelSpec, **kwargs: Any) -> BaseChatModel:

    token = kwargs.pop("api_key", None) or getattr(settings, "dharmamitra_token", None)
    if not token:
        raise ModelUnavailableError("DHARMAMITRA_TOKEN is required for 'dharamitra' model")

    base_url = kwargs.pop(
        "base_url",
        "https://dharmamitra.org/api-search/chat-translate/v1/chat/completions",
    )

    return DharmamitraModelWrapper(token=token, base_url=base_url)
