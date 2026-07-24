# Unified-Async-LLM-Client

## Pre-entrega 1: Cliente de LLM robusto y asíncrono

### Qué construir

Debes entregar un repositorio de código (o un archivo Python estructurado) que contenga la implementación de un **Unified Async LLM Client**.

Este artefacto debe ser una clase (o conjunto de clases) en **Python 3.12** que permita:

- **Intercambiabilidad:** Poder instanciar un proveedor (OpenAI o Anthropic) bajo una interfaz común.
- **Asincronía:** Todas las llamadas a modelos deben ser no bloqueantes (`async`/`await`).
- **Streaming:** Implementar un método que devuelva un generador asíncrono de tokens.
- **Validación:** Uso de Pydantic para definir la estructura de los mensajes de entrada y la configuración del modelo.

### Pasos sugeridos

1. **Estructura de datos:** Crea un archivo `schemas.py` con Pydantic para definir `ChatMessage` (`role`, `content`) y `ModelResponse`. Implementar esto primero evita el "error de diccionarios anidados" tan común en principiantes.
2. **La base asíncrona:** Define una clase base abstracta `BaseLLMClient` con un método `async def generate()`.
3. **Implementación del proveedor:** Crea `OpenAIClient` y `AnthropicClient` heredando de la base. Usa los SDKs oficiales (`openai` y `anthropic`) en sus versiones asíncronas (`AsyncOpenAI` y `AsyncAnthropic`).
4. **Lógica de streaming:** Implementa el generador usando `yield` dentro de un loop `async for` que recorra el stream del SDK.
5. **Script de validación:** Crea un archivo `main.py` simple que importe tus clientes, cargue el `.env` y realice una pregunta corta ("¿Qué es la entropía?") tanto en modo normal como en streaming.

### Errores comunes a evitar

- **Bloqueo del event loop:** Un error clásico de nivel intermedio es usar la versión síncrona del cliente dentro de una función `async`. Esto detiene todo el programa mientras el LLM "piensa". Asegúrate de usar `await client.chat.completions.create(...)`.
- **Fuga de excepciones:** No dejes que un error de "API Key inválida" o "Límite de cuota" rompa el loop principal. Captura la excepción y devuelve un mensaje estructurado o haz un reintento (retry).
