import asyncio

from config import LLM_PROVIDER
from manager import AsyncLLMManager
from schemas import ChatMessage, ErrorResponse, ModelParams


QUESTION = "¿Qué es la entropía?"


async def run_normal(manager: AsyncLLMManager, messages: list[ChatMessage]) -> None:
    print("\n=== Modo normal (generate) ===\n")
    result = await manager.generate(messages, ModelParams(temperature=0.7, max_tokens=512))

    if isinstance(result, ErrorResponse):
        print(f"[ERROR] {result.error_type}: {result.error}")
        return

    print(f"Proveedor: {result.provider}")
    print(f"Modelo: {result.model}")
    print(f"Respuesta:\n{result.content}")


async def run_streaming(manager: AsyncLLMManager, messages: list[ChatMessage]) -> None:
    print("\n=== Modo streaming ===\n")
    print("Respuesta: ", end="", flush=True)

    async for chunk in manager.stream(
        messages,
        ModelParams(temperature=0.7, max_tokens=512),
    ):
        if isinstance(chunk, ErrorResponse):
            print(f"\n[ERROR] {chunk.error_type}: {chunk.error}")
            return
        print(chunk, end="", flush=True)

    print()


async def main() -> None:
    print(f"Proveedor activo (LLM_PROVIDER): {LLM_PROVIDER}")
    manager = AsyncLLMManager()
    messages = [ChatMessage(role="user", content=QUESTION)]

    print(f"Pregunta: {QUESTION}")
    await run_normal(manager, messages)
    await run_streaming(manager, messages)


if __name__ == "__main__":
    asyncio.run(main())
