from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.core.security import obtener_usuario_actual
from app.db.models import Categoria, Gasto, Usuario
from app.db.session import get_db
from app.schemas.gasto import (
    GastoCreate,
    GastoResponse,
    ItemResumen,
    ResumenMensualResponse,
)

router = APIRouter(tags=["Gastos"])


@router.post(
    "/gastos", response_model=GastoResponse, status_code=status.HTTP_201_CREATED
)
def crear_gasto(
    payload: GastoCreate,
    response: Response,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """Crea y persiste un gasto del usuario autenticado.

    Args:
        payload: Datos validados del gasto, incluida su categoría.
        response: Respuesta HTTP donde se establece la cabecera ``Location``.
        db: Sesión SQLAlchemy usada para consultar y guardar el gasto.
        usuario_actual: Usuario autenticado propietario del nuevo gasto.

    Returns:
        La entidad ``Gasto`` creada, serializada como ``GastoResponse``.

    Raises:
        HTTPException: Con estado 422 si la categoría no existe.
        SQLAlchemyError: Si falla una operación de base de datos.
    """
    categoria = (
        db.query(Categoria)
        .filter(Categoria.id_categoria == payload.id_categoria)
        .first()
    )
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Elige una categoria",
        )

    nuevo_gasto = Gasto(
        id_usuario=usuario_actual.id_usuario,
        comercio=payload.comercio,
        fecha=payload.fecha,
        monto=payload.monto,
        id_categoria=payload.id_categoria,
    )
    db.add(nuevo_gasto)
    db.commit()
    db.refresh(nuevo_gasto)

    response.headers["Location"] = f"/gastos/{nuevo_gasto.id_gasto}"
    return nuevo_gasto


@router.get("/gastos", response_model=list[GastoResponse])
def listar_gastos(
    fecha: str | None = Query(None, description="Fecha en formato AAAA-MM-DD"),
    fecha_inicio: str | None = Query(None, description="Inicio del período AAAA-MM-DD"),
    fecha_fin: str | None = Query(None, description="Fin del período AAAA-MM-DD"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """Lista los gastos del usuario autenticado, opcionalmente por fecha.

    Args:
        fecha: Filtro opcional en formato ISO ``AAAA-MM-DD``.
        db: Sesión SQLAlchemy usada para consultar los gastos.
        usuario_actual: Usuario autenticado cuyos gastos se listan.

    Returns:
        Gastos ordenados por fecha e identificador descendentes.

    Raises:
        HTTPException: Con estado 400 si ``fecha`` no es una fecha ISO válida.
        SQLAlchemyError: Si falla la consulta de base de datos.
    """
    consulta = db.query(Gasto).filter(Gasto.id_usuario == usuario_actual.id_usuario)

    if fecha and (fecha_inicio or fecha_fin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use fecha o el rango fecha_inicio/fecha_fin, no ambos",
        )

    if fecha:
        try:
            fecha_filtro = date.fromisoformat(fecha)
            consulta = consulta.filter(Gasto.fecha == fecha_filtro)
        except ValueError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Utilice AAAA-MM-DD",
            ) from err

    if bool(fecha_inicio) != bool(fecha_fin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rango requiere fecha_inicio y fecha_fin",
        )

    if fecha_inicio and fecha_fin:
        try:
            inicio = date.fromisoformat(fecha_inicio)
            fin = date.fromisoformat(fecha_fin)
        except ValueError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Utilice AAAA-MM-DD",
            ) from err
        if inicio > fin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="fecha_inicio no puede ser posterior a fecha_fin",
            )
        consulta = consulta.filter(Gasto.fecha >= inicio, Gasto.fecha <= fin)

    return consulta.order_by(Gasto.fecha.desc(), Gasto.id_gasto.desc()).all()


@router.get("/gastos/{id_gasto}", response_model=GastoResponse)
def obtener_gasto(
    id_gasto: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """Obtiene un gasto que pertenece al usuario autenticado.

    Args:
        id_gasto: Identificador del gasto solicitado.
        db: Sesión SQLAlchemy usada para buscar el gasto.
        usuario_actual: Usuario autenticado que debe ser propietario del gasto.

    Returns:
        La entidad ``Gasto`` encontrada, serializada como ``GastoResponse``.

    Raises:
        HTTPException: Con estado 404 si el gasto no existe o pertenece a otro
            usuario.
        SQLAlchemyError: Si falla la consulta de base de datos.
    """
    gasto = (
        db.query(Gasto)
        .filter(
            Gasto.id_gasto == id_gasto, Gasto.id_usuario == usuario_actual.id_usuario
        )
        .first()
    )

    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Gasto no encontrado"
        )
    return gasto


@router.delete("/gastos/{id_gasto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_gasto(
    id_gasto: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
) -> Response:
    gasto = (
        db.query(Gasto)
        .filter(
            Gasto.id_gasto == id_gasto,
            Gasto.id_usuario == usuario_actual.id_usuario,
        )
        .first()
    )
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Gasto no encontrado"
        )

    db.delete(gasto)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/resumenes", response_model=ResumenMensualResponse)
def obtener_resumen_mensual(
    anio: int = Query(..., description="Año del resumen"),
    mes: int = Query(..., ge=1, le=12, description="Mes del resumen (1-12)"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """Calcula los totales y porcentajes por categoría de un mes.

    Args:
        anio: Año del resumen solicitado.
        mes: Mes del resumen, entre 1 y 12.
        db: Sesión SQLAlchemy usada para consultar los gastos.
        usuario_actual: Usuario autenticado cuyos gastos se agregan.

    Returns:
        Un ``ResumenMensualResponse`` con los totales del mes; si no hay gastos,
        contiene una lista vacía y un mensaje informativo.

    Raises:
        SQLAlchemyError: Si falla la consulta de base de datos. FastAPI responde
            422 antes de llamar esta función si falta ``anio`` o ``mes`` está
            fuera de rango.
    """
    gastos_mes = (
        db.query(
            Categoria.id_categoria,
            Categoria.nombre,
            func.sum(Gasto.monto).label("total_categoria"),
        )
        .join(Gasto, Gasto.id_categoria == Categoria.id_categoria)
        .filter(
            Gasto.id_usuario == usuario_actual.id_usuario,
            extract("year", Gasto.fecha) == anio,
            extract("month", Gasto.fecha) == mes,
        )
        .group_by(Categoria.id_categoria, Categoria.nombre)
        .all()
    )

    total_general = (
        sum(item.total_categoria for item in gastos_mes) if gastos_mes else 0.0
    )

    if total_general == 0:
        return ResumenMensualResponse(
            anio=anio,
            mes=mes,
            total_mes=0.0,
            items=[],
            mensaje="No hay gastos en este mes",
        )

    items = []
    for id_cat, nombre, total_cat in gastos_mes:
        pct = round((float(total_cat) / float(total_general)) * 100, 1)
        items.append(
            ItemResumen(
                id_categoria=id_cat,
                categoria=nombre,
                total=round(float(total_cat), 2),
                porcentaje=pct,
            )
        )

    return ResumenMensualResponse(
        anio=anio, mes=mes, total_mes=round(float(total_general), 2), items=items
    )
