# Criterios de aceptación — Control de gastos personales

## Alcance y fuentes

Este documento separa los criterios del registro de pruebas. Los criterios HU-02, HU-03, HU-04, HU-07 y HU-08 se transcriben de los escenarios documentados en [registro_pruebas.md](./registro_pruebas.md). No se encontró en el repositorio un documento original completo de historias de usuario; por eso, este archivo consolida únicamente reglas documentadas y aclaraciones confirmadas, sin afirmar que sea una transcripción de una fuente original.

La práctica adjunta de ventas fiadas no forma parte de este proyecto.

## Criterios confirmados

### HU-02 — Validación de fecha del gasto

- Con la fecha de referencia 24/10/2026, un gasto con fecha 15/10/2026 es válido y conserva esa fecha.
- Con esa misma fecha de referencia, un gasto con fecha 30/12/2026 se rechaza; la interfaz muestra `La fecha no puede ser posterior a hoy` y marca el campo de fecha en rojo.
- **Aclaración confirmada por el usuario el 26/11/2026:** una fecha igual a la fecha de referencia es válida.

### HU-03 — Validación y corrección del monto

- En la vista previa, corregir el monto leído de $58.000 a `85000` actualiza el monto mostrado a $85.000 sin volver a leer el recibo.
- Si se ingresa `abc` o `0`, la interfaz muestra exactamente `El monto debe ser un número mayor a 0` y restaura el último monto válido.
- En el backend, los valores no válidos se rechazan y no se guardan. La respuesta API para `abc` no tiene un mensaje exacto establecido por este criterio; el mensaje anterior corresponde a la vista previa.

### HU-04 — Categoría del gasto

- Al elegir «Comida» y guardar, el gasto queda asociado a esa categoría.
- Si falta la categoría, el gasto se rechaza, la interfaz muestra exactamente `Elige una categoría` y no se persiste.

### HU-07 — Tope mensual

- Definir un tope de $400.000 para «Comida» en octubre de 2026 lo guarda; la presentación documentada es `Comida: $0 de $400.000`.
- Los valores `-50000` y `0` se rechazan; la interfaz muestra exactamente `El tope debe ser mayor a $0`.

### HU-08 — Alertas de tope

- Con un tope de $400.000 para «Comida» y un acumulado de $325.000 (81 % según el escenario), se muestra la alerta exacta `Llevas el 81 % de tu tope en Comida`.
- Para «Ocio» sin tope y con un gasto de $50.000, no se muestra alerta; la interfaz indica `Sin tope definido`.
- **Aclaración confirmada por el usuario el 26/11/2026:** mostrar alerta cuando el porcentaje es menor o mayor que 80 %, pero no cuando es exactamente 80 %. Esta regla incluye el 0 %.
  - Exactamente 80 %: $320.000 de $400.000 — no alertar.
  - Por debajo de 80 %: $300.000 de $400.000 (75 %) — alertar.
- El texto de la alerta para porcentajes distintos del 81 % del escenario no está especificado.

## Reglas y datos aún no definidos

- No hay precisión mínima definida para el primer monto o tope positivo.
- No está definido el formato de alerta para porcentajes diferentes del 81 % documentado.
- Los requisitos de precisión/tiempo para lectura OCR requieren los recibos de prueba pendientes indicados en [PREGUNTAS.md](./PREGUNTAS.md).
- No se incorporan aquí historias con referencias parciales pero sin escenario y resultado esperado completos; no se deben inferir a partir de la implementación.
