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

---

## Entradas de la Semana 6 — 2026-11-14

### Entrada 4: Revisión de seguridad asistida por IA

- **Qué pedí:** Verificar los commits H-01, H-02 y H-03, revisar `.env.example`
  y las configuraciones de Ruff, y evaluar el uso de la clave de Gemini en la
  URL.
- **Qué respondió la IA:** Los cambios de clave JWT obligatoria, CORS limitado y
  manejo de errores de red se observaron en los diffs. También encontró que
  `.env.example` aún contenía un valor de demostración y que la clave Gemini
  seguía en `?key=` pese a enviarse también en un encabezado.
- **Qué verifiqué:** Comparé `git show` de los tres commits con los archivos
  actuales; confirmé la plantilla y comparé ambas configuraciones Ruff. Mi
  verificación personal: **[COMPLETAR POR MÍ]**.
- **Qué decidí:** Corregir la plantilla, mover la clave Gemini solo al
  encabezado y probar el cambio sin editar pruebas existentes.

### Entrada 5: Envío seguro de clave Gemini (H-06)

- **Qué pedí:** Confirmar si Gemini acepta la API key en `x-goog-api-key` y
  corregir la URL si era compatible.
- **Qué respondió la IA:** La documentación oficial de Gemini muestra ese
  encabezado para REST; propuso retirar el parámetro `?key=` y probar la
  solicitud con un cliente HTTP simulado.
- **Qué verifiqué:** Revisé el código y la documentación, añadí
  `backend/tests/test_receipt_reader_auth.py` y ejecuté la prueba nueva
  (3 pasadas, incluidas timeout y fallo de conexión) y la suite backend con
  base temporal limpia (15 pasadas). No hice una llamada real a Google ni usé
  una clave real. Mi verificación personal: **[COMPLETAR POR MÍ]**.
- **Qué decidí:** Aceptar el cambio, conservando el comportamiento de respuesta
  y registrándolo en el commit `db9f6d3`.

### Entrada 6: Trabajo del agente Antigravity CLI

- **Qué pedí al agente:** **[COMPLETAR POR MÍ: pegar la solicitud real enviada
  a Antigravity CLI]**.
- **Qué respondió el agente:** **[COMPLETAR POR MÍ: resumir su respuesta real;
  no inferirla solo a partir de los commits]**.
- **Qué verifiqué:** La rama actual es `semana6-revision`. Revisé con `git show`
  los diffs de `ade50ff`, `e6a41d6` y `9ef3d8a`, los contrasté con el código
  vigente y ejecuté las comprobaciones indicadas en el informe. Mi verificación
  personal del diff: **[COMPLETAR POR MÍ]**.
- **Qué decidí:** **[COMPLETAR POR MÍ: indicar qué sugerencias del agente
  acepté o rechacé y por qué]**.

### Entrada 7: Refactor de umbral de alerta

- **Qué pedí:** Revisar el backend en busca de valores mágicos y refactors
  pequeños sin alterar el comportamiento.
- **Qué respondió la IA:** Detectó que el umbral `80` estaba repetido en las
  dos rutas de topes; sugirió nombrarlo como constante. También observó una
  fórmula parecida de porcentaje, pero las respuestas usan precisión distinta.
- **Qué verifiqué:** Comparé el diff para confirmar que solo se reemplazó el
  literal por `UMBRAL_ALERTA_PORCENTAJE` y ejecuté Ruff y las pruebas backend.
  Mi verificación personal: **[COMPLETAR POR MÍ]**.
- **Qué decidí:** Aceptar el cambio mínimo en el commit `7633004`; no extraer la
  fórmula para no arriesgar la diferencia de redondeo entre endpoints.
