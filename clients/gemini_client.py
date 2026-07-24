from collections.abc import AsyncIterator

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from clients.base_client import BaseLLMClient
from config import DEFAULT_MODELS, GEMINI_API_KEY
from schemas import ChatMessage, ErrorResponse, ModelParams, ModelResponse


class GeminiClient(BaseLLMClient):
    """Cliente asíncrono para Gemini (google-genai)."""

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY no está configurada")
        self._client = genai.Client(api_key=key)
        self._provider = "gemini"

    def _resolve_params(self, params: ModelParams | None) -> ModelParams:
        if params is None:
            return ModelParams(model=DEFAULT_MODELS["gemini"])
        if params.model is None:
            return params.model_copy(update={"model": DEFAULT_MODELS["gemini"]})
        return params

    def _build_contents(
        self,
        messages: list[ChatMessage],
    ) -> tuple[str | None, list[types.Content]]:
        """Separa system_instruction; user→user, assistant→model."""
        system_parts: list[str] = []
        contents: list[types.Content] = []

        for message in messages:
            if message.role == "system":
                system_parts.append(message.content)
                continue

            role = "user" if message.role == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=message.content)],
                )
            )

        system = "\n\n".join(system_parts) if system_parts else None
        return system, contents

    def _build_config(
        self,
        resolved: ModelParams,
        system: str | None,
    ) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            temperature=resolved.temperature,
            max_output_tokens=resolved.max_tokens,
            system_instruction=system,
        )

    def _map_exception(self, exc: Exception) -> ErrorResponse:
        if isinstance(exc, genai_errors.ClientError):
            code = getattr(exc, "code", None)
            if code == 429:
                return ErrorResponse(error=str(exc), error_type="rate_limit")
            return ErrorResponse(error=str(exc), error_type="api_error")
        if isinstance(exc, genai_errors.ServerError):
            return ErrorResponse(error=str(exc), error_type="api_error")
        if isinstance(exc, genai_errors.APIError):
            return ErrorResponse(error=str(exc), error_type="api_error")
        if isinstance(exc, TimeoutError):
            return ErrorResponse(error=str(exc), error_type="timeout")
        if isinstance(exc, ConnectionError):
            return ErrorResponse(error=str(exc), error_type="connection")
        return ErrorResponse(error=str(exc), error_type="unknown")

    async def generate(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> ModelResponse | ErrorResponse:
        resolved = self._resolve_params(params)
        system, contents = self._build_contents(messages)

        try:
            response = await self._client.aio.models.generate_content(
                model=resolved.model,
                contents=contents,
                config=self._build_config(resolved, system),
            )
            finish_reason = None
            if response.candidates:
                finish_reason = str(response.candidates[0].finish_reason)

            return ModelResponse(
                content=response.text or "",
                model=resolved.model,
                provider=self._provider,
                finish_reason=finish_reason,
            )
        except (
            genai_errors.ClientError,
            genai_errors.ServerError,
            genai_errors.APIError,
            TimeoutError,
            ConnectionError,
        ) as exc:
            return self._map_exception(exc)

    async def stream(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> AsyncIterator[str | ErrorResponse]:
        resolved = self._resolve_params(params)
        system, contents = self._build_contents(messages)

        try:
            stream = await self._client.aio.models.generate_content_stream(
                model=resolved.model,
                contents=contents,
                config=self._build_config(resolved, system),
            )
            async for chunk in stream:
                text = chunk.text
                if text:
                    yield text
        except (
            genai_errors.ClientError,
            genai_errors.ServerError,
            genai_errors.APIError,
            TimeoutError,
            ConnectionError,
        ) as exc:
            yield self._map_exception(exc)
