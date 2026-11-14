import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY: str = os.getenv(
    "SECRET_KEY", "clave_secreta_super_segura_para_jwt_desarrollo_12345"
)
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gastos.db")

AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
