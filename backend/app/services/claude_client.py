from __future__ import annotations


import json
from collections.abc import AsyncGenerator
from typing import Literal, TypedDict

import httpx

from app.config import get_settings

ClaudeRole = Literal["user", "assistant"]


class ClaudeMessage(TypedDict):
    role: ClaudeRole
    content: str


class ClaudeClientError(Exception):
    pass


class ClaudeConfigurationError(ClaudeClientError):
    pass


class ClaudeAPIError(ClaudeClientError):
    pass

from app.config import get_settings

class ClaudeClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def stream_messages(
        self,
        *,
        system_prompt: str,
        messages: list[ClaudeMessage],
    ) -> AsyncGenerator[str, None]:
        if not self.settings.anthropic_api_key:
            raise ClaudeConfigurationError("ANTHROPIC_API_KEY .env ichida sozlanmagan.")

        payload = {
            "model": self.settings.claude_model,
            "max_tokens": self.settings.claude_max_tokens,
            "system": system_prompt,
            "messages": messages,
            "stream": True,
        }
        headers = {
            "x-api-key": self.settings.anthropic_api_key,
            "anthropic-version": self.settings.anthropic_api_version,
            "content-type": "application/json",
        }

        timeout = httpx.Timeout(connect=20.0, read=None, write=20.0, pool=20.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                self.settings.anthropic_api_url,
                headers=headers,
                json=payload,
            ) as response:
                if response.status_code >= 400:
                    await response.aread()
                    if response.status_code in {401, 403}:
                        raise ClaudeAPIError(
                            "Claude API autentifikatsiyasi amalga oshmadi. "
                            "ANTHROPIC_API_KEY qiymatini tekshiring."
                        )
                    if response.status_code == 429:
                        raise ClaudeAPIError(
                            "Claude API so'rovlar limiti vaqtincha tugadi. Birozdan keyin qayta urinib ko'ring."
                        )
                    raise ClaudeAPIError(f"Claude API vaqtincha ishlamadi (HTTP {response.status_code}).")

                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue

                    data = line.removeprefix("data:").strip()
                    if not data or data == "[DONE]":
                        continue

                    event = json.loads(data)
                    event_type = event.get("type")
                    if event_type == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta" and delta.get("text"):
                            yield delta["text"]
                    elif event_type == "error":
                        error = event.get("error", {})
                        raise ClaudeAPIError(error.get("message", "Claude streaming xatosi."))
                    elif event_type == "message_stop":
                        break

    async def complete_message(
        self,
        *,
        system_prompt: str,
        messages: list[ClaudeMessage],
    ) -> str:
        chunks = [
            chunk
            async for chunk in self.stream_messages(
                system_prompt=system_prompt,
                messages=messages,
            )
        ]
        return "".join(chunks).strip()


def get_claude_client() -> ClaudeClient:
    return ClaudeClient()
