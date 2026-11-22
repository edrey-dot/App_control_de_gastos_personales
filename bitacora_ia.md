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
El asistente de IA me ayudó a estructurar el flujo de trabajo, la arquitectura y las pruebas, definiendo un contrato claro con tipado estricto y planteando casos límite como años bisiestos y fechas idénticas al día de hoy. Las pruebas unitarias
fueron fundamentales para garantizar que el mensaje de error fuera idéntico al solicitado por el cliente y para
atrapar casos de borde como el día de mañana. En una próxima ocasión, definiría desde el inicio la estructura de
carpetas y repositorios para evitar reorganizaciones entre el frontend y el backend durante el desarrollo.

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
  verificación personal: abrí `config.py` y confirmé que `SECRET_KEY` ya no
  tiene valor por defecto; abrí `main.py` y vi que los orígenes de CORS son
  solo `localhost`. Corrí yo mismo `pytest`, `ruff check .` y `pip-audit`,
  porque el agente no pudo ejecutar `pip-audit` (no estaba instalado).
- **Qué decidí:** Corregir la plantilla, mover la clave Gemini solo al
  encabezado y probar el cambio sin editar pruebas existentes.

### Entrada 5: Envío seguro de clave Gemini (H-06)

- **Qué pedí:** Confirmar si Gemini acepta la API key en `x-goog-api-key` y
  corregir la URL si

---

## Entradas de la Semana 7 — 2026-11-22

### Entrada 6: Diseño de reglas y casos de prueba

- **Qué pedí:** Seleccionar funciones del proyecto con reglas de negocio y
  diseñar particiones, límites y una tabla de decisión desde las historias.
- **Qué respondió la IA:** Propuso HU-02, HU-03, HU-04, HU-07 y HU-08 como
  fuentes de casos, con HU-08 para las condiciones combinadas de tope y gasto.
- **Qué verifiqué:** Comparé cada esperado con las historias que compartí.
  Confirmé que la fecha igual a hoy, el 80 % exacto, el gasto menor al 80 % con
  tope y el formato de otros porcentajes no estaban aclarados.
- **Qué decidí:** Dejar esos casos como ambiguos, no asignarles un resultado
  esperado y probar solo los escenarios respaldados por la historia.

### Entrada 7: Generación, ejecución y auditoría de pruebas

- **Qué pedí:** Generar pruebas pytest parametrizadas, ejecutarlas y comprobar
  que detectaran fallos en las reglas.
- **Qué respondió la IA:** Añadió casos para fecha, monto, categoría, tope y
  alerta; incluyó comentarios por fila, `pytest.approx` en valores numéricos y
  `pytest.raises` con `ValueError` en la validación directa de fecha.
- **Qué verifiqué:** La primera ejecución encontró que el backend respondía
  `numero` y `categoria` sin tilde, aunque HU-03 y HU-04 especifican las formas
  con tilde. Se mantuvieron los esperados de las historias y se corrigieron los
  mensajes en backend e interfaz. Después, `pytest -v` pasó con 33 pruebas y
  Ruff pasó. Las tres mutaciones temporales fueron detectadas; tras restaurarlas
  la suite volvió a pasar.
- **Qué decidí:** Conservar los esperados originales y registrar en
  `registro_pruebas.md` los fallos iniciales, la corrección y las pruebas de
  sensibilidad.

### Entrada 8: Datos sintéticos con fixture

- **Qué pedí:** Preparar datos ficticios con casos de texto y valores límite,
  sin usar información real.
- **Qué respondió la IA:** Amplió el fixture local `contexto_sintetico` con
  `Mercado Ñandú d'Oliva`, una cadena vacía, cero, `abc` y el monto válido
  $85.000. El correo se genera de forma única bajo `@prueba.local`.
- **Qué verifiqué:** Las pruebas usan la base SQLite temporal configurada para
  pytest y las categorías de prueba; no utilizan las bases locales ni datos de
  personas reales o familiares. `pytest -v` pasó con 33 pruebas.
- **Qué decidí:** Usar los datos para las pruebas de API y documentar la cadena
  vacía como dato sintético sin expectativa, porque las historias compartidas
  no especifican el resultado de ese caso.