from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

import httpx

from ..exceptions import ProviderInvocationError


@dataclass
class SimpleResponse:
    """Minimal response carrying text content (mimics LLM message content)."""
    content: str


class DharmamitraModelWrapper:
    """
    Translation-only wrapper integrating Dharmamitra chat-translate API.
    Exposes invoke/ainvoke to match LangChain-style usage.
    """

    def __init__(self, token: str, base_url: str):
        self._token = token
        self._base_url = base_url

    # --------------------------
    # Input extraction / payload
    # --------------------------

    def _normalize_input_to_text(self, input: Union[str, List[Any]]) -> str:
        if isinstance(input, str):
            return input
        if isinstance(input, list) and input:
            # messages may have .content; fallback to str(m)
            return "\n".join([getattr(m, "content", str(m)) for m in input])
        return str(input)

    def _extract_source_and_lang(self, content: str) -> Tuple[str, str]:
        """
        Heuristic extraction based on your prompt conventions.
        - target language: "Translate the provided text into <LANG> while..."
        - source block: between 'SOURCE TEXT:' and 'Translation:' (end)
        """
        lang = "english"
        m_lang = re.search(
            r"Translate\s+the\s+provided\s+text\s+into\s+([A-Za-z\- ]+?)\s+while",
            content,
            re.IGNORECASE,
        )
        if m_lang:
            lang = (m_lang.group(1) or "english").strip().lower()

        src = content
        m_src = re.search(
            r"SOURCE\s+TEXT:\s*(.*?)\s*Translation:\s*\Z",
            content,
            re.IGNORECASE | re.DOTALL,
        )
        if m_src:
            src = m_src.group(1).strip()

        return src, lang

    def _headers(self, stream: bool) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        if stream:
            headers["Accept"] = "text/event-stream"
        return headers

    def _payload(self, source_text: str, target_lang: str, stream: bool) -> Dict[str, Any]:
        return {
            "model": "mitra-base",
            "messages": [{"role": "user", "content": source_text}],
            "stream": bool(stream),
            "do_grammar": False,
            "input_encoding": "auto",
            "target_lang": (target_lang or "english").lower(),
        }

    # --------------------------
    # Parsing helpers
    # --------------------------

    def _append_from_obj(self, chunks: List[str], obj: Any) -> None:
        """
        Try OpenAI-like streaming delta shapes or generic fields.
        """
        if not isinstance(obj, dict):
            return

        choices = obj.get("choices")
        if isinstance(choices, list):
            for ch in choices:
                if not isinstance(ch, dict):
                    continue
                delta = ch.get("delta")
                if isinstance(delta, dict) and isinstance(delta.get("content"), str):
                    chunks.append(delta["content"])
                    continue
                msg = ch.get("message")
                if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                    chunks.append(msg["content"])
                    continue

        if isinstance(obj.get("content"), str):
            chunks.append(obj["content"])
        elif isinstance(obj.get("text"), str):
            chunks.append(obj["text"])

    def _parse_non_stream(self, data: Any, fallback_text: str) -> str:
        if isinstance(data, dict):
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    msg = first.get("message")
                    if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                        return msg["content"].strip()
            if isinstance(data.get("content"), str):
                return data["content"].strip()
            if isinstance(data.get("text"), str):
                return data["text"].strip()
        return (fallback_text or "").strip()

    # --------------------------
    # Core translate routines
    # --------------------------

    def _translate_stream_sync(self, source_text: str, target_lang: str) -> str:
        payload = self._payload(source_text, target_lang, stream=True)
        chunks: List[str] = []

        with httpx.Client(timeout=None) as client:
            with client.stream("POST", self._base_url, headers=self._headers(stream=True), json=payload) as resp:
                resp.raise_for_status()
                for raw_line in resp.iter_lines():
                    if not raw_line:
                        continue
                    line = raw_line.decode("utf-8", errors="ignore") if isinstance(raw_line, (bytes, bytearray)) else str(raw_line)
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if not data_str or data_str == "[DONE]":
                        continue
                    try:
                        obj = json.loads(data_str)
                        self._append_from_obj(chunks, obj)
                    except json.JSONDecodeError:
                        # Sometimes providers emit plain text in data: lines
                        chunks.append(data_str)

        return "".join(chunks).strip()

    async def _translate_stream_async(self, source_text: str, target_lang: str) -> str:
        payload = self._payload(source_text, target_lang, stream=True)
        chunks: List[str] = []

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", self._base_url, headers=self._headers(stream=True), json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if not data_str or data_str == "[DONE]":
                        continue
                    try:
                        obj = json.loads(data_str)
                        self._append_from_obj(chunks, obj)
                    except json.JSONDecodeError:
                        chunks.append(data_str)

        return "".join(chunks).strip()

    def _translate_non_stream_sync(self, source_text: str, target_lang: str) -> str:
        payload = self._payload(source_text, target_lang, stream=False)
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(self._base_url, headers=self._headers(stream=False), json=payload)
            resp.raise_for_status()
            try:
                return self._parse_non_stream(resp.json(), resp.text)
            except Exception:
                return (resp.text or "").strip()

    async def _translate_non_stream_async(self, source_text: str, target_lang: str) -> str:
        payload = self._payload(source_text, target_lang, stream=False)
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self._base_url, headers=self._headers(stream=False), json=payload)
            resp.raise_for_status()
            try:
                return self._parse_non_stream(resp.json(), resp.text)
            except Exception:
                return (resp.text or "").strip()

    # --------------------------
    # Public API (LangChain-like)
    # --------------------------

    def invoke(self, input: Union[str, List[Any]], **kwargs: Any) -> SimpleResponse:
        content = self._normalize_input_to_text(input)
        source_text, target_lang = self._extract_source_and_lang(content)

        try:
            text = self._translate_stream_sync(source_text, target_lang)
            if not text:
                text = self._translate_non_stream_sync(source_text, target_lang)
            return SimpleResponse(text)
        except Exception as e:
            raise ProviderInvocationError(f"Dharmamitra invocation failed: {e}") from e

    async def ainvoke(self, input: Union[str, List[Any]], **kwargs: Any) -> SimpleResponse:
        content = self._normalize_input_to_text(input)
        source_text, target_lang = self._extract_source_and_lang(content)

        try:
            text = await self._translate_stream_async(source_text, target_lang)
            if not text:
                text = await self._translate_non_stream_async(source_text, target_lang)
            return SimpleResponse(text)
        except Exception as e:
            raise ProviderInvocationError(f"Dharmamitra invocation failed: {e}") from e

    def with_structured_output(self, schema: Any):
        raise ValueError("'dharamitra' supports translation only; structured outputs are not available.")
