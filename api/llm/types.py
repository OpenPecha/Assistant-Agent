from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence

from langchain_core.language_models import BaseChatModel


BuildFn = Callable[..., BaseChatModel]


@dataclass(frozen=True)
class ModelSpec:
    name: str 
    provider: str 
    required_credential: Optional[str] = None
    build: BuildFn = None
    description: str = ""
    capabilities: Sequence[str] = field(default_factory=tuple)
    context_window: Optional[int] = None
    aliases: Sequence[str] = field(default_factory=tuple)
    provider_model_name: Optional[str] = None
