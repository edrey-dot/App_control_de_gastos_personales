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

def test_hu02_escenario_1_fecha_pasada_es_valida():
    """HU-02 Escenario 1: Una fecha en el pasado respecto a 'hoy' es válida."""
    hoy_simulado = date(2026, 10, 24)
    fecha_gasto = date(2026, 10, 15)

    resultado = validar_fecha_gasto(fecha_gasto, hoy=hoy_simulado)

    assert resultado == fecha_gasto


def test_hu02_fecha_pasada_sin_parametro_hoy_usa_fecha_actual():
    """HU-02 Caso normal: Cuando no se pasa 'hoy', toma date.today() por defecto."""
    fecha_pasada = date(2020, 1, 1)

    resultado = validar_fecha_gasto(fecha_pasada)

    assert resultado == fecha_pasada


# ==============================================================================
# Casos Límite (Al menos 2)
# ==============================================================================

def test_hu02_limite_fecha_igual_a_hoy_es_valida():
    """HU-02 Caso límite: Una fecha exactamente igual al umbral 'hoy' es válida."""
    hoy_simulado = date(2026, 10, 24)
    fecha_hoy = date(2026, 10, 24)

    resultado = validar_fecha_gasto(fecha_hoy, hoy=hoy_simulado)

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

def test_hu02_escenario_2_error_fecha_futura_rechazada_con_mensaje_exacto():
    """HU-02 Escenario 2: Rechaza fecha futura con el mensaje exacto especificado."""
    hoy_simulado = date(2026, 10, 24)
    fecha_futura = date(2026, 12, 30)
    mensaje_esperado = "La fecha no puede ser posterior a hoy"

    with pytest.raises(ValueError) as exc_info:
        validar_fecha_gasto(fecha_futura, hoy=hoy_simulado)

    assert str(exc_info.value) == mensaje_esperado


def test_hu02_limite_error_fecha_de_manana_es_rechazada():
    """HU-02 Caso límite de error: El día inmediatamente siguiente (mañana) es rechazado."""
    hoy_simulado = date(2026, 10, 24)
    fecha_manana = hoy_simulado + timedelta(days=1)
    mensaje_esperado = "La fecha no puede ser posterior a hoy"

    with pytest.raises(ValueError) as exc_info:
        validar_fecha_gasto(fecha_manana, hoy=hoy_simulado)

    assert str(exc_info.value) == mensaje_esperado
