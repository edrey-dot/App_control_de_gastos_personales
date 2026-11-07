# Bitácora de Uso de Asistente de IA

Registro de interacciones, sugerencias del asistente y decisiones de diseño tomadas durante el desarrollo guiado por TDD para la **Funcionalidad de la semana 5**.

---

## Entradas de Interacción

### Entrada 1: Contrato e inyección de fecha de referencia (HU-02)
- Decisión: Aceptada
- Razón: Permite aplicar una inyección de dependencias simple. Hace que la función sea pura y permite probar fechas
  fijas (como el 24/10/2026 del criterio Gherkin) de manera determinística, sin depender del reloj del sistema ni
  requerir librerías externas
- Cómo se verificó: Se probó pasando hoy=date(2026, 10, 24) en las pruebas unitarias y verificando que fechas
  pasadas y futuras se evaluaran respecto a ese día fijo

---

### Entrada 2: Suite de pruebas unitarias primero (HU-02 - Fase Roja)
- Decisión: Aceptada
- Razón: Garantiza el cumplimiento estricto de TDD. Diseñar primero casos normales, casos límite (el día de hoy y
  años bisiestos) y casos de error con el texto exacto asegura que el código solo haga lo necesario sin
  sobreingeniería.
- Cómo se verificó: Se ejecutó pytest desde App_gastos/backend, comprobando que las 6 pruebas fallaron limpiamente
  por NotImplementedError sin errores de importación ni de sintaxis.

---

### Entrada 3: Refactorización: extracción de constante y eliminación de reasignación (HU-02)
- Decisión: Aceptada
- Razón: Elimina cadenas mágicas ("magic strings") del código fuente y facilita que la capa de API
  (FastAPI/Pydantic) reutilice la misma constante de error. Además, evita reasignar parámetros de entrada (hoy),
  siguiendo buenas prácticas de inmutabilidad.
- Cómo se verificó: Se ejecutó pytest -v y las 6 pruebas pasaron al 100% en verde en 0.12 segundos sin haber tenido
  que modificar ninguna prueba.

---


## Reflexión Final del Estudiante (5 a 8 líneas)
El asistente de IA me ayudó a estructurar el flujo de trabajo, la aruquitectura, las implementar las pruebas, definiendo un contrato claro con tipado estricto y planteando casos límite como años bisiestos y fechas idénticas al día de hoy. Las pruebas unitarias
fueron fundamentales para garantizar que el mensaje de error fuera idéntico al solicitado por el cliente y para
atrapar casos de borde como el día de mañana. En una próxima ocasión, definiría desde el inicio la estructura de
carpetas y repositorios para evitar reorganizaciones entre el frontend y el backend durante el desarrollo."
