from collections.abc import AsyncIterator

import anthropic
from anthropic import AsyncAnthropic

from clients.base_client import BaseLLMClient
from config import ANTHROPIC_API_KEY, DEFAULT_MODELS
from schemas import ChatMessage, ErrorResponse, ModelParams, ModelResponse


class AnthropicClient(BaseLLMClient):
    """Cliente asíncrono para Anthropic (AsyncAnthropic)."""

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or ANTHROPIC_API_KEY
        if not key:
            raise ValueError("ANTHROPIC_API_KEY no está configurada")
        self._client = AsyncAnthropic(api_key=key)
        self._provider = "anthropic"

    def _resolve_params(self, params: ModelParams | None) -> ModelParams:
        if params is None:
            return ModelParams(model=DEFAULT_MODELS["anthropic"])
        if params.model is None:
            return params.model_copy(update={"model": DEFAULT_MODELS["anthropic"]})
        return params

    def _split_messages(
        self,
        messages: list[ChatMessage],
    ) -> tuple[str | None, list[dict[str, str]]]:
        """Anthropic usa `system` aparte; en `messages` solo user/assistant."""
        system_parts: list[str] = []
        chat_messages: list[dict[str, str]] = []

        for message in messages:
            if message.role == "system":
                system_parts.append(message.content)
                continue
            chat_messages.append({"role": message.role, "content": message.content})

        system = "\n\n".join(system_parts) if system_parts else None
        return system, chat_messages

    def _map_exception(self, exc: Exception) -> ErrorResponse:
        if isinstance(exc, anthropic.RateLimitError):
            return ErrorResponse(error=str(exc), error_type="rate_limit")
        if isinstance(exc, anthropic.APITimeoutError):
            return ErrorResponse(error=str(exc), error_type="timeout")
        if isinstance(exc, anthropic.APIConnectionError):
            return ErrorResponse(error=str(exc), error_type="connection")
        if isinstance(exc, anthropic.APIError):
            return ErrorResponse(error=str(exc), error_type="api_error")
        return ErrorResponse(error=str(exc), error_type="unknown")

    async def generate(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> ModelResponse | ErrorResponse:
        resolved = self._resolve_params(params)
        system, chat_messages = self._split_messages(messages)

        kwargs: dict = {
            "model": resolved.model,
            "messages": chat_messages,
            "temperature": resolved.temperature,
            "max_tokens": resolved.max_tokens,
        }
        if system:
            kwargs["system"] = system

        try:
            response = await self._client.messages.create(**kwargs)
            text_parts = [
                block.text
                for block in response.content
                if getattr(block, "type", None) == "text"
            ]
            return ModelResponse(
                content="".join(text_parts),
                model=response.model,
                provider=self._provider,
                finish_reason=response.stop_reason,
            )
        except (
            anthropic.RateLimitError,
            anthropic.APITimeoutError,
            anthropic.APIConnectionError,
            anthropic.APIError,
        ) as exc:
            return self._map_exception(exc)

    async def stream(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> AsyncIterator[str | ErrorResponse]:
        resolved = self._resolve_params(params)
        system, chat_messages = self._split_messages(messages)

        kwargs: dict = {
            "model": resolved.model,
            "messages": chat_messages,
            "temperature": resolved.temperature,
            "max_tokens": resolved.max_tokens,
        }
        if system:
            kwargs["system"] = system

        try:
            async with self._client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    if text:
                        yield text
        except (
            anthropic.RateLimitError,
            anthropic.APITimeoutError,
            anthropic.APIConnectionError,
            anthropic.APIError,
        ) as exc:
            yield self._map_exception(exc)
