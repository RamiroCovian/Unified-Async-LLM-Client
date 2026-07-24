from collections.abc import AsyncIterator

from clients.anthropic_client import AnthropicClient
from clients.base_client import BaseLLMClient
from clients.gemini_client import GeminiClient
from clients.openai_client import OpenAIClient
from config import LLM_PROVIDER
from schemas import ChatMessage, ErrorResponse, ModelParams, ModelResponse


class AsyncLLMManager:
    """
    Facade que instancia el cliente correcto según LLM_PROVIDER
    (openai | anthropic | gemini) y expone generate/stream unificados.
    """

    _SUPPORTED = frozenset({"openai", "anthropic", "gemini"})

    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or LLM_PROVIDER or "openai").strip().lower()
        self._client = self._build_client()

    def _build_client(self) -> BaseLLMClient:
        if self.provider not in self._SUPPORTED:
            raise ValueError(
                f"Proveedor no soportado: '{self.provider}'. "
                f"Usa uno de: {', '.join(sorted(self._SUPPORTED))}"
            )

        if self.provider == "openai":
            return OpenAIClient()
        if self.provider == "anthropic":
            return AnthropicClient()
        return GeminiClient()

    @property
    def client(self) -> BaseLLMClient:
        return self._client

    async def generate(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> ModelResponse | ErrorResponse:
        return await self._client.generate(messages, params)

    def stream(
        self,
        messages: list[ChatMessage],
        params: ModelParams | None = None,
    ) -> AsyncIterator[str | ErrorResponse]:
        return self._client.stream(messages, params)
