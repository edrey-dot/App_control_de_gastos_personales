from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, categorias, gastos, recibos, topes
from app.db.models import Categoria
from app.db.session import Base, SessionLocal, engine


def inicializar_bd():
    """Crea las tablas y siembra las categorías por defecto."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        categorias_iniciales = ["Comida", "Transporte", "Ocio"]
        for nombre in categorias_iniciales:
            existe = db.query(Categoria).filter(Categoria.nombre == nombre).first()
            if not existe:
                db.add(Categoria(nombre=nombre))
        db.commit()
    finally:
        db.close()


# Ejecutar inicialización de la base de datos
inicializar_bd()


@asynccontextmanager
async def lifespan(app: FastAPI):
    inicializar_bd()
    yield


app = FastAPI(
    title="API de Control de Gastos Personales",
    description=(
        "Backend FastAPI con autenticación JWT, registro de gastos y lectura con IA"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configuración de CORS para permitir la conexión desde Ionic / Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Location"],
)


# Manejador personalizado de errores de validación
@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    """Distingue entre 400 (campos extra prohibidos / JSON mal formado)
    y 422 (validaciones de negocio con mensaje exacto).
    """
    errores = exc.errors()

    for err in errores:
        # Detectar campos extra prohibidos (R-03, HU-09: extra='forbid')
        if err.get("type") == "extra_forbidden":
            campo = err.get("loc", ["campo"])[-1]
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": f"Campo no permitido: {campo}"},
            )

        # Errores con mensaje personalizado de negocio
        msg = err.get("msg", "")
        # Extraer mensaje si viene prefijado por pydantic 'Value error, ...'
        if "Value error, " in msg:
            msg = msg.replace("Value error, ", "")

        # Si el error es de fecha, monto o categoría, retornar 422 con el mensaje exacto
        if msg in [
            "La fecha no puede ser posterior a hoy",
            "El monto debe ser un numero mayor a 0",
            "Elige una categoria",
            "El tope debe ser mayor a $0",
            "El comercio es obligatorio",
        ]:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": msg},
            )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": errores}
    )


# Registrar routers
app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(gastos.router)
app.include_router(topes.router)
app.include_router(recibos.router)


@app.get("/", tags=["Salud"])
def raiz():
    return {
        "sistema": "Control de Gastos Personales API",
        "estado": "operativo",
        "documentacion": "/docs",
    }
