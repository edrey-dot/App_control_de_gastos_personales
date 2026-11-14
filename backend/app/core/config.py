import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# H-01: Exigir SECRET_KEY obligatoria sin fallback hardcodeado predecible
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError(
        "Error de seguridad: La variable de entorno SECRET_KEY es obligatoria. "
        "Defina una clave secreta segura en el archivo .env o en el entorno."
    )

ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gastos.db")

AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# H-02: Orígenes permitidos para CORS (configurable por entorno)
CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:4200,http://localhost:8100,http://localhost,capacitor://localhost",
    ).split(",")
    if origin.strip()
]
