# Bitácora de Uso de Asistente de IA

Registro de interacciones, sugerencias del asistente y decisiones de diseño tomadas durante el desarrollo guiado por TDD para la **Funcionalidad de la semana 5**.

---

## Entradas de Interacción

### Entrada 1: Contrato e inyección de fecha de referencia (HU-02)
- **Fecha:** 2026-11-07
- **Sugerencia del asistente:** Definir la función pura `validar_fecha_gasto(fecha: date, hoy: Optional[date] = None) -> date`, inyectando `hoy` con valor por defecto `None` (tomando `date.today()`) para permitir pruebas unitarias determinísticas con fechas fijas (ej. `24/10/2026`) sin efectos secundarios ni mocks globales.
- **Decisión:** `[BORRADOR: Aceptada / Ajustada / Rechazada]`
- **Razón:** `[BORRADOR: Justificación técnica del estudiante sobre por qué se tomó esta decisión]`
- **Cómo se verificó:** `[BORRADOR: Cómo comprobó el estudiante que funcionaba]`

---

### Entrada 2: Suite de pruebas unitarias primero (HU-02 - Fase Roja)
- **Fecha:** 2026-11-07
- **Sugerencia del asistente:** Crear 6 pruebas unitarias antes de la implementación: 2 casos normales (pasado con `hoy` inyectado y sin `hoy`), 2 casos límite (fecha igual al umbral `hoy` y fecha en año bisiesto), y 2 casos de error (fecha futura del criterio Gherkin y fecha de mañana) verificando el mensaje exacto `"La fecha no puede ser posterior a hoy"`.
- **Decisión:** `[BORRADOR: Aceptada / Ajustada / Rechazada]`
- **Razón:** `[BORRADOR: Justificación del estudiante sobre la cobertura y diseño de los tests]`
- **Cómo se verificó:** `[BORRADOR: Ejecución de pytest mostrando que las pruebas fallaron por NotImplementedError sin errores de sintaxis ni de importación]`

---

### Entrada 3: Refactorización: extracción de constante y eliminación de reasignación (HU-02)
- **Fecha:** 2026-11-07
- **Sugerencia del asistente:** Extraer la cadena mágica `"La fecha no puede ser posterior a hoy"` a la constante de módulo `ERROR_FECHA_POSTERIOR_A_HOY` para facilitar su reutilización en FastAPI/Pydantic, y reemplazar la mutación de `hoy` por una variable local inmutable `fecha_referencia`.
- **Decisión:** `[BORRADOR: Aceptada / Ajustada / Rechazada]`
- **Razón:** `[BORRADOR: Justificación del estudiante sobre buenas prácticas de clean code]`
- **Cómo se verificó:** `[BORRADOR: Ejecución de pytest asegurando que todas las 6 pruebas pasaron al 100% sin modificar los tests]`

---

## Preguntas abiertas / Decisiones del Estudiante para HU-02
1. **Manejo de strings vs date:** ¿Prefieres que `validar_fecha_gasto` sea estrictamente de objetos `date` (delegando a Pydantic la conversión en la API REST), o que la función también acepte strings en formato ISO (ej. `"2026-10-15"`) y los parsee internamente?
   - *Decisión del estudiante:* `[Pendiente de responder]`

---

## Reflexión Final del Estudiante (5 a 8 líneas)
*(Espacio reservado exclusivamente para la reflexión personal del estudiante sobre: en qué ayudó el asistente, qué error atraparon las pruebas y qué haría diferente)*

```text
[Escribe aquí tu reflexión personal de 5 a 8 líneas]
```
