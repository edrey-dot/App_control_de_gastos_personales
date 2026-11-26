from math import floor

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.core.security import obtener_usuario_actual
from app.db.models import Categoria, Gasto, TopeMensual, Usuario
from app.db.session import get_db
from app.schemas.tope import TopeCreate, TopeResponse

router = APIRouter(prefix="/topes", tags=["Topes Mensuales"])

UMBRAL_ALERTA_PORCENTAJE = 80


def _debe_mostrar_alerta_80(porcentaje: float) -> bool:
    # Regla confirmada: alertar bajo y sobre 80 %, salvo justo en 80 %.
    return porcentaje != UMBRAL_ALERTA_PORCENTAJE


@router.put("", response_model=TopeResponse, status_code=status.HTTP_200_OK)
def definir_tope(
    payload: TopeCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """Crea o actualiza el tope mensual de una categoría del usuario.

    Args:
        payload: Categoría, año, mes y monto del tope validados.
        db: Sesión SQLAlchemy usada para consultar y guardar el tope.
        usuario_actual: Usuario autenticado propietario del tope.

    Returns:
        Un ``TopeResponse`` con el monto gastado, porcentaje y alerta calculados.

    Raises:
        SQLAlchemyError: Si falla una operación de base de datos. FastAPI
            responde 422 antes de llamar esta función si el cuerpo no es válido.
    """
    tope = (
        db.query(TopeMensual)
        .filter(
            TopeMensual.id_usuario == usuario_actual.id_usuario,
            TopeMensual.id_categoria == payload.id_categoria,
            TopeMensual.anio == payload.anio,
            TopeMensual.mes == payload.mes,
        )
        .first()
    )

    if not tope:
        tope = TopeMensual(
            id_usuario=usuario_actual.id_usuario,
            id_categoria=payload.id_categoria,
            anio=payload.anio,
            mes=payload.mes,
            monto_tope=payload.monto_tope,
        )
        db.add(tope)
    else:
        tope.monto_tope = payload.monto_tope

    db.commit()
    db.refresh(tope)

    categoria = (
        db.query(Categoria)
        .filter(Categoria.id_categoria == payload.id_categoria)
        .first()
    )
    nombre_categoria = categoria.nombre if categoria else ""

    # Calcular gasto actual
    total_gastado = (
        db.query(func.sum(Gasto.monto))
        .filter(
            Gasto.id_usuario == usuario_actual.id_usuario,
            Gasto.id_categoria == payload.id_categoria,
            extract("year", Gasto.fecha) == payload.anio,
            extract("month", Gasto.fecha) == payload.mes,
        )
        .scalar()
    ) or 0.0

    porcentaje_raw = (float(total_gastado) / float(payload.monto_tope)) * 100
    porcentaje = floor(porcentaje_raw)
    alerta_80 = _debe_mostrar_alerta_80(porcentaje_raw)
    mensaje_alerta = (
        f"Llevas el {porcentaje} % de tu tope en {nombre_categoria}"
        if alerta_80
        else None
    )

    return TopeResponse(
        id_categoria=payload.id_categoria,
        categoria=nombre_categoria,
        anio=payload.anio,
        mes=payload.mes,
        monto_tope=float(payload.monto_tope),
        total_gastado=round(float(total_gastado), 2),
        porcentaje=porcentaje_raw,
        alerta_80=alerta_80,
        mensaje_alerta=mensaje_alerta,
    )


@router.get("", response_model=list[TopeResponse])
def listar_topes(
    anio: int = Query(...),
    mes: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """Lista los topes del usuario para un mes con gasto y alerta calculados.

    Args:
        anio: Año consultado.
        mes: Mes consultado, entre 1 y 12.
        db: Sesión SQLAlchemy usada para consultar topes y gastos.
        usuario_actual: Usuario autenticado cuyos topes se listan.

    Returns:
        Una lista de ``TopeResponse`` con totales y alertas por categoría.

    Raises:
        SQLAlchemyError: Si falla una consulta de base de datos. FastAPI
            responde 422 antes de llamar esta función si falta ``anio`` o
            ``mes`` está fuera de rango.
    """
    topes = (
        db.query(TopeMensual, Categoria.nombre)
        .join(Categoria, Categoria.id_categoria == TopeMensual.id_categoria)
        .filter(
            TopeMensual.id_usuario == usuario_actual.id_usuario,
            TopeMensual.anio == anio,
            TopeMensual.mes == mes,
        )
        .all()
    )

    resultado = []
    for tope, nombre_categoria in topes:
        total_gastado = (
            db.query(func.sum(Gasto.monto))
            .filter(
                Gasto.id_usuario == usuario_actual.id_usuario,
                Gasto.id_categoria == tope.id_categoria,
                extract("year", Gasto.fecha) == anio,
                extract("month", Gasto.fecha) == mes,
            )
            .scalar()
        ) or 0.0

        porcentaje_raw = (float(total_gastado) / float(tope.monto_tope)) * 100
        porcentaje_entero = floor(porcentaje_raw)
        alerta_80 = _debe_mostrar_alerta_80(porcentaje_raw)
        mensaje_alerta = (
            f"Llevas el {porcentaje_entero} % de tu tope en {nombre_categoria}"
            if alerta_80
            else None
        )

        resultado.append(
            TopeResponse(
                id_categoria=tope.id_categoria,
                categoria=nombre_categoria,
                anio=tope.anio,
                mes=tope.mes,
                monto_tope=float(tope.monto_tope),
                total_gastado=round(float(total_gastado), 2),
                porcentaje=round(porcentaje_raw, 1),
                alerta_80=alerta_80,
                mensaje_alerta=mensaje_alerta,
            )
        )

    return resultado
