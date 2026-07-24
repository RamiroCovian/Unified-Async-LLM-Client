from collections.abc import AsyncIterator

import openai
from openai import AsyncOpenAI

from clients.base_client import BaseLLMClient
from config import DEFAULT_MODELS, OPENAI_API_KEY
from schemas import ChatMessage, ErrorResponse, ModelParams, ModelResponse


class OpenAIClient(BaseLLMClient):
    """Cliente asíncrono para OpenAI (AsyncOpenAI)."""

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or OPENAI_API_KEY
        if not key:
            raise ValueError("OPENAI_API_KEY no está configurada")
        self._client = AsyncOpenAI(api_key=key)
        self._provider = "openai"

    def _resolve_params(self, params: ModelParams | None) -> ModelParams:
        if params is None:
            return ModelParams(model=DEFAULT_MODELS["openai"])
        if params.model is None:
            return params.model_copy(update={"model": DEFAULT_MODELS["openai"]})
        return params

    def _to_openai_messages(self, messages: list[ChatMessage]) -> list[dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in messages]

    def _map_exception(self, exc: Exception) -> ErrorResponse:
        if isinstance(exc, openai.RateLimitError):
            return ErrorResponse(error=str(exc), error_type="rate_limit")
        if isinstance(exc, openai.APITimeoutError):
            return ErrorResponse(error=str(exc), error_type="timeout")
        if isinstance(exc, openai.APIConnectionError):
            return ErrorResponse(error=str(exc), error_type="connection")
        if isinstance(exc, openai.APIError):
            return ErrorResponse(error=str(exc), error_type="api_error")
        return ErrorResponse(error=str(exc), error_type="unknown")

    async def generate(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> ModelResponse | ErrorResponse:
        resolved = self._resolve_params(params)
        try:
            response = await self._client.chat.completions.create(
                model=resolved.model,
                messages=self._to_openai_messages(messages),
                temperature=resolved.temperature,
                max_tokens=resolved.max_tokens,
            )
            choice = response.choices[0]
            return ModelResponse(
                content=choice.message.content or "",
                model=response.model,
                provider=self._provider,
                finish_reason=choice.finish_reason,
            )
        except (
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.APIError,
        ) as exc:
            return self._map_exception(exc)

    async def stream(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> AsyncIterator[str | ErrorResponse]:
        resolved = self._resolve_params(params)
        try:
            stream = await self._client.chat.completions.create(
                model=resolved.model,
                messages=self._to_openai_messages(messages),
                temperature=resolved.temperature,
                max_tokens=resolved.max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except (
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.APIError,
        ) as exc:
            yield self._map_exception(exc)
