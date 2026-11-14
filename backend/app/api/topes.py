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


@router.put("", response_model=TopeResponse, status_code=status.HTTP_200_OK)
def definir_tope(
    payload: TopeCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    """HU-07: Definir o actualizar tope mensual para una categoría."""
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
    alerta_80 = porcentaje >= UMBRAL_ALERTA_PORCENTAJE
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
    """HU-07 & HU-08: Listar todos los topes del mes
    con sus porcentajes y alertas calculadas.
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
        alerta_80 = porcentaje_entero >= UMBRAL_ALERTA_PORCENTAJE
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
