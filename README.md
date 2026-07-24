# Unified-Async-LLM-Client

Cliente LLM unificado y asíncrono para **OpenAI**, **Anthropic** y **Gemini**, con validación Pydantic, streaming y manejo controlado de errores.

## Requisitos

- Python 3.12+
- Una API key del proveedor que vayas a usar

## 1. Crear el entorno virtual

Desde la raíz del repositorio:

```bash
python -m venv env
```

Activar el entorno:

**Windows (PowerShell):**

```powershell
.\env\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source env/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## 2. Variables de entorno

Copiá el ejemplo y completá tus claves:

```bash
cp .env.example .env
```

Contenido de `.env`:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu_api_key_gemini
OPENAI_API_KEY=tu_api_key_openai
ANTHROPIC_API_KEY=tu_api_key_anthropic
```

| Variable | Descripción |
|----------|-------------|
| `LLM_PROVIDER` | Proveedor activo: `openai`, `anthropic` o `gemini` |
| `OPENAI_API_KEY` | Clave de OpenAI (si usás `openai`) |
| `ANTHROPIC_API_KEY` | Clave de Anthropic (si usás `anthropic`) |
| `GEMINI_API_KEY` | Clave de Google Gemini (si usás `gemini`) |

Solo necesitás la API key del proveedor elegido en `LLM_PROVIDER`.

## 3. Ejecutar el script de prueba

Con el entorno activado y el `.env` configurado:

```bash
python main.py
```

El script pregunta **"¿Qué es la entropía?"** en:

1. **Modo normal** (`generate`) — respuesta completa
2. **Modo streaming** — tokens a medida que llegan

## Estructura

```
├── main.py                 # Script de prueba
├── manager.py              # AsyncLLMManager (elige el proveedor)
├── config.py               # Carga de .env y defaults
├── schemas.py              # Modelos Pydantic
├── clients/
│   ├── base_client.py      # Interfaz común
│   ├── openai_client.py
│   ├── anthropic_client.py
│   └── gemini_client.py
├── requirements.txt
└── .env.example
```

## Uso rápido en código

```python
import asyncio
from manager import AsyncLLMManager
from schemas import ChatMessage, ErrorResponse, ModelParams

async def demo():
    manager = AsyncLLMManager()  # lee LLM_PROVIDER del .env
    messages = [ChatMessage(role="user", content="Hola")]

    result = await manager.generate(messages, ModelParams())
    if isinstance(result, ErrorResponse):
        print(result.error_type, result.error)
    else:
        print(result.content)

asyncio.run(demo())
```
