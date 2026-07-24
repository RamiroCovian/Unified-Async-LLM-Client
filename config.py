import os
from dotenv import load_dotenv

# Cargo variables definidas en el archivo .env al entorno del proceso
load_dotenv()

# Lee la API key del LLM PROVIDER desde el entorno
API_KEY = os.getenv("LLM_PROVIDER", "gemini")
