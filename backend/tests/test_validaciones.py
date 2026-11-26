"""Pruebas unitarias para la validación de fecha de gastos (HU-02).

Criterios de aceptación (HU-02):
- Escenario 1: Fecha pasada o presente es válida y se conserva.
- Escenario 2 (error): Fecha posterior a hoy es rechazada con el mensaje
  exacto "La fecha no puede ser posterior a hoy".
"""

from datetime import date, timedelta

import pytest
from app.domain.validaciones import validar_fecha_gasto

# ==============================================================================
# Casos Normales (Al menos 2)
# ==============================================================================


@pytest.mark.parametrize(
    ("fecha_gasto", "hoy_simulado", "esperada", "error_esperado"),
    [
        # HU-02 escenario 1: el 15/10/2026 está en el pasado respecto al 24/10/2026.
        (date(2026, 10, 15), date(2026, 10, 24), date(2026, 10, 15), None),
        # HU-02 escenario 2: el 30/12/2026 es futuro respecto al 24/10/2026.
        (
            date(2026, 12, 30),
            date(2026, 10, 24),
            None,
            "La fecha no puede ser posterior a hoy",
        ),
    ],
)
def test_hu02_reglas_de_fecha_de_las_historias(
    fecha_gasto, hoy_simulado, esperada, error_esperado
):
    """Comprueba los dos escenarios de fecha explícitos en HU-02."""
    # Dado: la fecha del gasto y «hoy» de los escenarios HU-02.
    # Cuando: se valida la fecha con una referencia determinista.
    if error_esperado is None:
        # Entonces: la fecha pasada se conserva.
        assert validar_fecha_gasto(fecha_gasto, hoy=hoy_simulado) == esperada
    else:
        # Entonces: la fecha futura se rechaza con el mensaje exacto.
        with pytest.raises(ValueError) as exc_info:
            validar_fecha_gasto(fecha_gasto, hoy=hoy_simulado)

        assert str(exc_info.value) == error_esperado


def test_hu02_fecha_pasada_sin_parametro_hoy_usa_fecha_actual():
    """HU-02 Caso normal: Cuando no se pasa 'hoy', toma date.today() por defecto."""
    fecha_pasada = date(2020, 1, 1)

    resultado = validar_fecha_gasto(fecha_pasada)

    assert resultado == fecha_pasada


# ==============================================================================
# Casos Límite (Al menos 2)
# ==============================================================================


def test_hu02_limite_fecha_igual_a_hoy_es_valida():
    """Aclaración confirmada: una fecha igual a hoy es válida."""
    hoy_simulado = date(2026, 10, 24)
    fecha_hoy = date(2026, 10, 24)

    # Dado: hoy es 24/10/2026 y el gasto tiene esa misma fecha.
    # Cuando: se valida la fecha con la referencia confirmada por el usuario.
    resultado = validar_fecha_gasto(fecha_hoy, hoy=hoy_simulado)

    # Entonces: la fecha igual a hoy se conserva como válida.
    assert resultado == fecha_hoy


def test_hu02_limite_bisiesto_fin_de_mes_es_valida():
    """HU-02 Caso límite: Fecha límite de fin de mes en año bisiesto pasado es válida."""
    hoy_simulado = date(2026, 10, 24)
    fecha_bisiesto = date(2024, 2, 29)

    resultado = validar_fecha_gasto(fecha_bisiesto, hoy=hoy_simulado)

    assert resultado == fecha_bisiesto


# ==============================================================================
# Casos de Error (Mensaje exacto según criterio de aceptación)
# ==============================================================================


def test_hu02_limite_error_fecha_de_manana_es_rechazada():
    """HU-02 Caso límite de error: El día inmediatamente siguiente (mañana) es rechazado."""
    hoy_simulado = date(2026, 10, 24)
    fecha_manana = hoy_simulado + timedelta(days=1)
    mensaje_esperado = "La fecha no puede ser posterior a hoy"

    # Dado: hoy es 24/10/2026 y el gasto tiene fecha 25/10/2026.
    # Cuando: se valida la fecha del día siguiente.
    with pytest.raises(ValueError) as exc_info:
        validar_fecha_gasto(fecha_manana, hoy=hoy_simulado)

    # Entonces: se rechaza con el mensaje requerido para una fecha futura.
    assert str(exc_info.value) == mensaje_esperado
