# Control de Gastos Personales con Escáner de Facturas

Aplicación para la gestión y control de gastos personales mediante el escaneo de facturas y recibos físicos, desarrollada con Ionic + Angular para el frontend y FastAPI (Python) para el backend con PostgreSQL.

---

## Funcionalidad de la semana 5

Esta sección documenta la implementación guiada por TDD (Test-Driven Development) de las funciones puras del dominio para las historias de usuario de prioridad MUST, cumpliendo con la entrega de la **Semana 5**.

### HU-02: Confirmar en vista previa antes de guardar (Validación de fecha)

#### 1. Historia de usuario y criterios de aceptación
- **ID:** `HU-02` (Prioridad: MUST)
- **Historia:** Como usuario, quiero confirmar los datos en una vista previa antes de guardar el gasto para evitar guardar datos mal leídos.
- **Criterio de aceptación (Escenario 2 - Error / Fecha futura):**
  - **Dado que** hoy es `24/10/2026` y la vista previa muestra la fecha `30/12/2026`,
  - **cuando** toco "Guardar",
  - **entonces** la app marca la fecha en rojo, muestra `"La fecha no puede ser posterior a hoy"` y no guarda el gasto.
- **Criterio de aceptación (Escenario 1 - Confirmar fecha válida):**
  - **Dado que** la vista previa muestra comercio "Supermercado Central", fecha `15/10/2026` y monto `$85.000`,
  - **cuando** toco "Guardar",
  - **entonces** el gasto aparece en la lista del `15/10/2026` con `$85.000`.

---

#### 2. Contrato de la función

- **Ubicación del módulo:** `backend/app/domain/validaciones.py`
- **Nombre de la función:** `validar_fecha_gasto`
- **Firma:**
  ```python
  from datetime import date
  from typing import Optional

  def validar_fecha_gasto(fecha: date, hoy: Optional[date] = None) -> date:
  ```
- **Parámetros:**
  - `fecha` (`datetime.date`): Fecha del gasto que se desea registrar o validar.
  - `hoy` (`Optional[datetime.date]`, por defecto `None`): Fecha de referencia que representa el día actual. Si no se suministra (`None`), la función toma automáticamente `date.today()`.
- **Retorno:**
  - `datetime.date`: Devuelve el mismo objeto `fecha` recibido si es válido (es decir, si `fecha <= hoy`).
- **Excepciones lanzadas:**
  - `ValueError`: Si `fecha > hoy`, lanza un `ValueError` con el mensaje exacto:
    `"La fecha no puede ser posterior a hoy"`.
  - `TypeError`: Si `fecha` no es una instancia de `date` o `hoy` no es `date` ni `None`.
- **Supuestos:**
  - La función pertenece a la capa de dominio pura: no realiza llamadas a red, base de datos ni servicios externos.
  - El parámetro `hoy` permite inyectar fechas específicas en pruebas automatizadas de manera determinística (por ejemplo, simular el día `24/10/2026`).
  - Un gasto puede ser del día de hoy (`fecha == hoy`) o de cualquier fecha en el pasado (`fecha < hoy`).
- **Casos límite:**
  - `fecha == hoy`: La fecha del gasto es exactamente hoy. Debe ser admitida como válida.
  - `fecha == hoy + 1 día`: La fecha es inmediatamente posterior (mañana). Debe lanzar `ValueError`.
  - `fecha` en el pasado lejano: Es válida cronológicamente (menor a hoy).
  - Fechas de fin de mes y años bisiestos (ej. 29 de febrero): Se validan correctamente respetando el calendario provisto por `datetime.date`.
- **Ejemplos de entrada y salida:**
  1. **Ejemplo 1 (Gasto en fecha pasada):**
     - Entrada: `fecha = date(2026, 10, 15)`, `hoy = date(2026, 10, 24)`
     - Salida: `date(2026, 10, 15)`
  2. **Ejemplo 2 (Gasto con fecha de hoy - Caso límite):**
     - Entrada: `fecha = date(2026, 10, 24)`, `hoy = date(2026, 10, 24)`
     - Salida: `date(2026, 10, 24)`
  3. **Ejemplo 3 (Gasto con fecha futura - Caso de error):**
     - Entrada: `fecha = date(2026, 12, 30)`, `hoy = date(2026, 10, 24)`
     - Salida: Lanza `ValueError("La fecha no puede ser posterior a hoy")`
  4. **Ejemplo 4 (Uso con valor por defecto de `hoy`):**
     - Entrada: `fecha = date(2020, 1, 1)` (sin pasar `hoy`)
     - Salida: `date(2020, 1, 1)` (asumiendo que la fecha actual es posterior al 2020)

---

#### 3. Cómo ejecutar las pruebas

Desde la carpeta `backend/`:

```bash
# Ejecutar todas las pruebas con pytest
pytest

# O ejecutando detalladamente las pruebas de dominio:
pytest tests/test_validaciones.py -v
```
