from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from schemas import ChatMessage, ErrorResponse, ModelParams, ModelResponse


class BaseLLMClient(ABC):
    """Contrato común para todos los proveedores LLM."""

    @abstractmethod
    async def generate(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> ModelResponse | ErrorResponse:
        """Respuesta completa (no streaming)."""
        pass

    @abstractmethod
    def stream(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> AsyncIterator[str | ErrorResponse]:
        """Generador async de tokens (async for chunk in client.stream(...))."""
        pass
