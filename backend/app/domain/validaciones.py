"""Módulo de validaciones de dominio para gastos personales.

Contiene funciones puras para validar reglas de negocio sin dependencias
de base de datos, red ni servicios externos.
"""

from datetime import date
from typing import Optional

# Constante de dominio para evitar cadenas mágicas y permitir reutilización
ERROR_FECHA_POSTERIOR_A_HOY: str = "La fecha no puede ser posterior a hoy"


def validar_fecha_gasto(fecha: date, hoy: Optional[date] = None) -> date:
    """Valida que la fecha de un gasto no sea posterior a hoy.

    Regla de negocio HU-02:
    - La fecha puede ser igual a hoy o de cualquier día en el pasado.
    - Si la fecha es posterior a hoy, lanza ValueError con el mensaje exacto:
      "La fecha no puede ser posterior a hoy".

    :param fecha: Fecha del gasto que se desea registrar.
    :param hoy: Fecha de referencia actual. Si es None, utiliza date.today().
    :return: La fecha validada.
    :raises ValueError: Si la fecha es posterior a 'hoy'.
    """
    fecha_referencia = date.today() if hoy is None else hoy

    if fecha > fecha_referencia:
        raise ValueError(ERROR_FECHA_POSTERIOR_A_HOY)

    return fecha
