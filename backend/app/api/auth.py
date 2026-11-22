from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import (
    crear_token_acceso,
    obtener_usuario_actual,
    obtener_contrasena_hash,
    verificar_contrasena,
)
from app.db.models import PerfilUsuario, Usuario
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    Token,
    UsuarioCreate,
    UsuarioResponse,
    normalizar_telefono_colombiano,
)
from app.schemas.perfil import PerfilResponse, PerfilUpdate

router = APIRouter(tags=["Autenticación"])
MAX_FOTO_PERFIL_BYTES = 2 * 1024 * 1024


def _nombre_predeterminado(usuario: Usuario) -> str:
    return usuario.correo.split("@", maxsplit=1)[0][:50]


def _respuesta_perfil(usuario: Usuario, perfil: PerfilUsuario | None) -> PerfilResponse:
    return PerfilResponse(
        id_usuario=usuario.id_usuario,
        nombre_usuario=(
            perfil.nombre_usuario if perfil else _nombre_predeterminado(usuario)
        ),
        correo=usuario.correo,
        telefono=perfil.telefono if perfil else None,
        tiene_foto=bool(perfil and perfil.foto_perfil),
    )


def _obtener_o_crear_perfil(
    usuario: Usuario, db: Session
) -> PerfilUsuario:
    perfil = db.query(PerfilUsuario).filter_by(id_usuario=usuario.id_usuario).first()
    if perfil is None:
        perfil = PerfilUsuario(
            id_usuario=usuario.id_usuario,
            nombre_usuario=_nombre_predeterminado(usuario),
        )
        db.add(perfil)
    return perfil


@router.post(
    "/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED
)
def registrar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un usuario y almacena el hash de su contraseña.

    Args:
        payload: Correo y contraseña validados para el registro.
        db: Sesión SQLAlchemy usada para buscar y guardar el usuario.

    Returns:
        La entidad ``Usuario`` creada, serializada sin su hash de contraseña.

    Raises:
        HTTPException: Con estado 409 si el correo ya está registrado.
        SQLAlchemyError: Si falla una operación de base de datos.
        Errores de Passlib o bcrypt: Si falla el cálculo del hash de contraseña.
        FastAPI responde 422 antes de llamar esta función si el cuerpo es
        inválido.
    """
    usuario_existente = (
        db.query(Usuario).filter(Usuario.correo == payload.correo).first()
    )
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado",
        )

    telefono_existente = (
        db.query(PerfilUsuario).filter_by(telefono=payload.telefono).first()
        if payload.telefono
        else None
    )
    if telefono_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El celular ya está registrado",
        )

    nuevo_usuario = Usuario(
        correo=payload.correo,
        contrasena_hash=obtener_contrasena_hash(payload.contrasena),
    )
    db.add(nuevo_usuario)
    db.flush()
    db.add(
        PerfilUsuario(
            id_usuario=nuevo_usuario.id_usuario,
            nombre_usuario=(
                payload.nombre_usuario or _nombre_predeterminado(nuevo_usuario)
            ),
            telefono=payload.telefono,
        )
    )
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/sesiones", response_model=Token)
def iniciar_sesion(payload: LoginRequest, db: Session = Depends(get_db)):
    """Autentica al usuario y crea un token de acceso JWT.

    Args:
        payload: Correo y contraseña enviados para iniciar sesión.
        db: Sesión SQLAlchemy usada para buscar el usuario.

    Returns:
        Un ``Token`` con el JWT de acceso y el tipo ``bearer``.

    Raises:
        HTTPException: Con estado 401 si el usuario no existe o la contraseña
            no coincide.
        SQLAlchemyError: Si falla la consulta de base de datos. Los errores de
            Passlib al verificar el hash y de PyJWT al firmar el token no se
            capturan y se propagan.
    """
    identificador = payload.identificador.strip()
    if "@" in identificador:
        usuario = (
            db.query(Usuario)
            .filter(Usuario.correo == identificador.lower())
            .first()
        )
    else:
        try:
            telefono = normalizar_telefono_colombiano(identificador)
        except ValueError:
            telefono = None
        usuario = (
            db.query(Usuario)
            .join(PerfilUsuario)
            .filter(PerfilUsuario.telefono == telefono)
            .first()
            if telefono
            else None
        )

    if not usuario or not verificar_contrasena(
        payload.contrasena, usuario.contrasena_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = crear_token_acceso(
        data={"sub": usuario.correo, "id_usuario": usuario.id_usuario}
    )
    return Token(access_token=token, token_type="bearer")


@router.get("/usuarios/me", response_model=PerfilResponse)
def obtener_perfil(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    perfil = db.query(PerfilUsuario).filter_by(id_usuario=usuario.id_usuario).first()
    return _respuesta_perfil(usuario, perfil)


@router.put("/usuarios/me", response_model=PerfilResponse)
def actualizar_perfil(
    payload: PerfilUpdate,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    perfil = _obtener_o_crear_perfil(usuario, db)
    if "telefono" in payload.model_fields_set:
        telefono_existente = (
            db.query(PerfilUsuario)
            .filter(
                PerfilUsuario.telefono == payload.telefono,
                PerfilUsuario.id_usuario != usuario.id_usuario,
            )
            .first()
            if payload.telefono
            else None
        )
        if telefono_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El celular ya está registrado",
            )
        perfil.telefono = payload.telefono
    perfil.nombre_usuario = payload.nombre_usuario
    db.commit()
    db.refresh(perfil)
    return _respuesta_perfil(usuario, perfil)


@router.put("/usuarios/me/foto", response_model=PerfilResponse)
async def actualizar_foto_perfil(
    foto: UploadFile = File(...),
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    tipos_validos = {
        "image/jpeg": lambda contenido: contenido.startswith(b"\xff\xd8\xff"),
        "image/png": lambda contenido: contenido.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": lambda contenido: (
            len(contenido) >= 12
            and contenido[:4] == b"RIFF"
            and contenido[8:12] == b"WEBP"
        ),
    }
    tipo = foto.content_type or ""
    validar_contenido = tipos_validos.get(tipo)
    if not validar_contenido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La foto debe ser JPG, PNG o WebP",
        )

    contenido = await foto.read(MAX_FOTO_PERFIL_BYTES + 1)
    if len(contenido) > MAX_FOTO_PERFIL_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="La foto no puede superar 2 MB",
        )
    if not validar_contenido(contenido):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido no coincide con el tipo de imagen",
        )

    perfil = _obtener_o_crear_perfil(usuario, db)
    perfil.foto_perfil = contenido
    perfil.tipo_foto_perfil = tipo
    db.commit()
    db.refresh(perfil)
    return _respuesta_perfil(usuario, perfil)


@router.get("/usuarios/me/foto")
def obtener_foto_perfil(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    perfil = db.query(PerfilUsuario).filter_by(id_usuario=usuario.id_usuario).first()
    if not perfil or not perfil.foto_perfil or not perfil.tipo_foto_perfil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay foto de perfil",
        )
    return Response(
        content=perfil.foto_perfil,
        media_type=perfil.tipo_foto_perfil,
        headers={"Cache-Control": "private, no-store"},
    )
