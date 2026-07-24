from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from schemas import ChatMessage, ModelParams, ModelResponse


class BaseLLMClient(ABC):
    """Contrato común para todos los proveedores LLM."""

    @abstractmethod
    async def generate(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> ModelResponse:
        """Respuesta completa (no streaming)."""
        pass

    @abstractmethod
    def stream(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> AsyncIterator[str]:
        """Generador async de tokens (async for chunk in client.stream(...))."""
        pass
