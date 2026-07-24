import os
from dotenv import load_dotenv

# Cargo variables definidas en el archivo .env al entorno del proceso
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Modelos default por proveedor (Los clientes los usan si ModelParams.model es None)
DEFAULT_MODELS = {
    "gemini": "gemini-3.1-flash-lite",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3.5-haiku-lastest",
}

DEFAULT_MODEL = DEFAULT_MODELS.get(LLM_PROVIDER, "gemini-3.1-flash-lite")
