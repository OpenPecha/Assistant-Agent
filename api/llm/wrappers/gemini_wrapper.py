from __future__ import annotations

from typing import Any, Dict, Optional


class GeminiModelWrapper:


    def __init__(self, base_model: Any, default_generation_config: Optional[Dict[str, Any]] = None):
        self._base = base_model
        self._default_gc = default_generation_config or {}

        self._structured_gc = {
            k: v for k, v in self._default_gc.items()
            if k not in ("response_mime_type",)
        }

    def __getattr__(self, item: str) -> Any:
        return getattr(self._base, item)

    def _merge_gc(self, kwargs: Dict[str, Any], structured: bool = False) -> Dict[str, Any]:
        user_gc = kwargs.get("generation_config") or {}
        merged = {**(self._structured_gc if structured else self._default_gc), **user_gc}

        if merged.get("response_mime_type") == "text/plain":
            merged.pop("response_mime_type", None)

        return merged

    def _call_with_retry_drop_thinking(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Some LangChain versions/providers may reject thinking_config.
        We try once with thinking_config, and if it errors, retry without it.
        """
        method = getattr(self._base, method_name)

        try:
            return method(*args, **kwargs)
        except TypeError as e:
            # common signature mismatch
            if "thinking_config" not in (kwargs.get("generation_config") or {}):
                raise
            gc = dict(kwargs.get("generation_config") or {})
            gc.pop("thinking_config", None)
            kwargs["generation_config"] = gc
            return method(*args, **kwargs)
        except ValueError as e:
            # sometimes provider validation errors
            if "thinking" not in str(e).lower():
                raise
            gc = dict(kwargs.get("generation_config") or {})
            gc.pop("thinking_config", None)
            kwargs["generation_config"] = gc
            return method(*args, **kwargs)

    def invoke(self, input: Any, **kwargs: Any) -> Any:
        kwargs["generation_config"] = self._merge_gc(kwargs)
        return self._call_with_retry_drop_thinking("invoke", input, **kwargs)

    async def ainvoke(self, input: Any, **kwargs: Any) -> Any:
        kwargs["generation_config"] = self._merge_gc(kwargs)
        method = getattr(self._base, "ainvoke")
        try:
            return await method(input, **kwargs)
        except TypeError:
            gc = dict(kwargs.get("generation_config") or {})
            gc.pop("thinking_config", None)
            kwargs["generation_config"] = gc
            return await method(input, **kwargs)
        except ValueError as e:
            if "thinking" not in str(e).lower():
                raise
            gc = dict(kwargs.get("generation_config") or {})
            gc.pop("thinking_config", None)
            kwargs["generation_config"] = gc
            return await method(input, **kwargs)

    async def abatch(self, inputs: Any, **kwargs: Any) -> Any:
        kwargs["generation_config"] = self._merge_gc(kwargs)
        method = getattr(self._base, "abatch")
        try:
            return await method(inputs, **kwargs)
        except TypeError:
            gc = dict(kwargs.get("generation_config") or {})
            gc.pop("thinking_config", None)
            kwargs["generation_config"] = gc
            return await method(inputs, **kwargs)

    def with_structured_output(self, schema: Any) -> "GeminiModelWrapper":
        structured = self._base.with_structured_output(schema)
        return GeminiModelWrapper(structured, default_generation_config=self._structured_gc)

    def astream(self, input: Any, **kwargs: Any):
        kwargs["generation_config"] = self._merge_gc(kwargs)
        # return async generator directly
        return self._base.astream(input, **kwargs)

    def astream_events(self, input: Any, **kwargs: Any):
        kwargs["generation_config"] = self._merge_gc(kwargs)
        return self._base.astream_events(input, **kwargs)
