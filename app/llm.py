"""OpenAI-compatible generation clients, instantiated only on demand."""

from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    def complete(
        self, *, model: str, messages: list[dict[str, str]], temperature: float = 0, json_mode: bool = False
    ) -> str: ...


class OpenAIClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        from openai import OpenAI

        self._client = OpenAI(base_url=base_url, api_key=api_key)

    def complete(
        self, *, model: str, messages: list[dict[str, str]], temperature: float = 0, json_mode: bool = False
    ) -> str:
        kwargs: dict[str, object] = {"model": model, "messages": messages, "temperature": temperature}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self._client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
