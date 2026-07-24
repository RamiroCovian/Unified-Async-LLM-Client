# Pre-entrega 1: Cliente de LLM robusto y asíncrono

## Qué construir

Debes entregar un repositorio de código (o un archivo Python estructurado) que contenga la implementación de un **Unified Async LLM Client**.

Este artefacto debe ser una clase (o conjunto de clases) en **Python 3.12** que permita:

- **Intercambiabilidad:** poder instanciar un proveedor (OpenAI o Anthropic) bajo una interfaz común.
- **Asincronía:** todas las llamadas a modelos deben ser no bloqueantes (`async` / `await`).
- **Streaming:** implementar un método que devuelva un generador asíncrono de tokens.
- **Validación:** uso de Pydantic para definir la estructura de los mensajes de entrada y la configuración del modelo.

## Pasos sugeridos

1. **Estructura de datos:** crea un archivo `schemas.py` con Pydantic para definir `ChatMessage` (`role`, `content`) y `ModelResponse`. Implementar esto primero evita el "error de diccionarios anidados" tan común en principiantes.
2. **La base asíncrona:** define una clase base abstracta `BaseLLMClient` con un método `async def generate()`.
3. **Implementación del proveedor:** crea `OpenAIClient` y `AnthropicClient` heredando de la base. Usa los SDKs oficiales (`openai` y `anthropic`) en sus versiones asíncronas (`AsyncOpenAI` y `AsyncAnthropic`).
4. **Lógica de streaming:** implementa el generador usando `yield` dentro de un loop `async for` que recorra el stream del SDK.
5. **Script de validación:** crea un archivo `main.py` simple que importe tus clientes, cargue el `.env` y realice una pregunta corta ("¿Qué es la entropía?") tanto en modo normal como en streaming.

## Errores comunes a evitar

- **Bloqueo del event loop:** un error clásico de nivel intermedio es usar la versión síncrona del cliente dentro de una función `async`. Esto detiene todo el programa mientras el LLM "piensa". Asegurate de usar `await client.chat.completions.create(...)`.
- **Fuga de excepciones:** no dejes que un error de "API Key inválida" o "Límite de cuota" rompa el loop principal. Capturá la excepción y devolvé un mensaje estructurado o hacé un reintento (retry).

## Consignas del entregable

1. Configurá un entorno virtual con Python 3.12 e instalá `openai`, `anthropic`, `pydantic` y `python-dotenv`.
2. Creá un esquema de Pydantic para validar los parámetros de entrada del modelo (temperatura de 0 a 2, `max_tokens`, etc.).
3. Implementá una clase `AsyncLLMManager` que pueda cargar tanto OpenAI como Anthropic basándose en una variable de configuración.
4. El método de generación debe ser capaz de manejar streaming: usá `yield` para retornar fragmentos de texto conforme lleguen de la API.
5. Asegurate de capturar excepciones de red y de límite de tasa (rate limiting) devolviendo un error controlado en lugar de un crash.
6. Incluí un archivo `README.md` que explique cómo ejecutar el script de prueba y qué variables de entorno son necesarias.
