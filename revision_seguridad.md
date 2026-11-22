# Revisión de seguridad — Semana 6

**Proyecto:** Control de gastos personales  
**Estudiante:** Yeison Edrey Rodriguez Hernandez  
**Fecha:** 2026-11-14  
**Commit revisado:** `35e3f1f`

## 1. Herramientas, criterios y revisión base

- **Linter:** Ruff **0.17.5** con las reglas **E, F, B, S**. Configuración en `pyproject.toml` (las configuraciones de la raíz y de `backend` son idénticas). `ruff check .` pasó sin avisos.
- **Auditoría de dependencias:** `pip-audit` **2.10.1**: **No known vulnerabilities found**.
- **Lista de revisión:** la de la semana 6 (corrección y pruebas, diseño y legibilidad, seguridad).
- **Revisión con IA:** Antigravity CLI, con un prompt por fases (ver sección 3).
- **Pruebas:** la suite backend pasó **15/15** tras borrar `backend/gastos.db` antes de ejecutar (ver H-07).

Se revisaron los cinco controles de la semana:

| Punto | ¿Aplica? | Resultado |
|---|---|---|
| Inyección | Sí | Consultas por ORM SQLAlchemy con parámetros; no se encontró SQL por concatenación (`backend/app/api/gastos.py:46`). |
| Secretos | Sí | `.env` no está versionado; `.env.example` deja `SECRET_KEY=` vacía (`backend/.env.example:2`). Ver H-01. |
| Contraseñas | Sí | Passlib/bcrypt con sal y mínimo de 8 caracteres (`backend/app/core/security.py:12`, `backend/app/schemas/auth.py:21`). |
| Acceso | Sí | Filtros por usuario autenticado; gasto ajeno devuelve 404 (`backend/app/api/gastos.py:129`). Pruebas de abuso en `test_seguridad_abuso.py`. |
| Dependencias | Sí | 11 requisitos fijados con `==`; auditoría limpia. |

**Claves reales de Gemini/OpenAI expuestas: ninguna detectada** en el historial de Git revisado. No se halló un archivo `.env` versionado; sin embargo, sí se había versionado el fallback JWT fijo y predecible de H-01. No sería correcto afirmar que nunca se subió ningún valor de clave. El fallback y el valor de demostración de la plantilla se eliminaron.

## 2. Hallazgos y avisos de linter

| Id | Archivo y línea | Problema | OWASP | Severidad | Corrección | Commit |
|---|---|---|---|---|---|---|
| H-01 | `backend/app/core/config.py:10`; `backend/.env.example:2` | Fallback JWT predecible | A02 Cryptographic Failures | Alta | Clave obligatoria; plantilla vacía | `ade50ff`, `e981df2` |
| H-02 | `backend/app/main.py:51` | CORS permisivo (`"*"` con credenciales) | A05 Security Misconfiguration | Media | Orígenes, métodos y encabezados limitados | `e6a41d6` |
| H-03 | `backend/app/services/receipt_reader.py:153` | Timeout y errores de red sin manejo controlado | Sin correspondencia directa; robustez | Media | Manejo controlado y pruebas de regresión | `9ef3d8a`, `2e06162` |
| H-04 | `backend/tests/test_seguridad_abuso.py:14` | Faltaban pruebas de abuso y aislamiento | A01 Broken Access Control (brecha de pruebas) | Media | Cuatro pruebas nuevas | `38fc0e6`, `caaa892` |
| H-05 | `backend/requirements.txt:11` | Dependencias con rango abierto (`>=`) | A06 Vulnerable and Outdated Components | Baja | Versiones exactas; multipart `==0.0.32` | `f0a1122`, `89eaa10` |
| H-06 | `backend/app/services/receipt_reader.py:121` | Clave Gemini en `?key=` | A02 Cryptographic Failures | Baja | Solo `x-goog-api-key`; prueba nueva | `db9f6d3` |
| H-07 | `backend/app/core/config.py:20`; `backend/tests/test_api_endpoints.py:13` | Pruebas acumulan datos en SQLite compartida | No aplica; aislamiento de pruebas | Baja | Pendiente: base temporal por suite | — |

Avisos no corregidos y justificación:

| Regla | Archivo y línea | Por qué se mantiene |
|---|---|---|
| B008 | `backend/app/api/` | Falso positivo por `Depends`, `Query` y `File` de FastAPI. |
| S101 | `backend/tests/` | `assert` es el uso esperado en pruebas pytest. |
| S105/S106 | `backend/app/api/auth.py`, `backend/app/schemas/auth.py` | `bearer` es el tipo de token OAuth2, no un secreto. |
| E501 | `backend/tests/test_validaciones.py:54,81` | Dos docstrings originales largos; se conservaron intactos. |

**Refactor sin cambio funcional:** se nombró el umbral `80` como `UMBRAL_ALERTA_PORCENTAJE` (`backend/app/api/topes.py:14`, commit `7633004`). La fórmula de porcentaje se repite, pero los endpoints devuelven precisión distinta; no se extrajo para evitar alterar el comportamiento.

**Verificación personal:**

- **H-01:** leí `config.py:10` en la versión original y el valor por defecto existía. Ahora la aplicación falla si falta la variable.
- **H-02:** leí `main.py:48` en la versión original y tenía `"*"` con credenciales. Ahora solo permite los orígenes del frontend.
- **H-03:** leí `receipt_reader.py:72` en la versión original y no había `try/except`. Ahora captura timeout y error de red.
- **H-04:** comprobé que no había pruebas de abuso. Las 4 nuevas pasan.
- **H-05:** `requirements.txt` tenía `>=`. Ahora tiene `==` y `pip-audit` no reporta vulnerabilidades.
- **H-06:** busqué `?key=` y confirmé que ya no está en la URL.

## 3. Revisión con IA

**Herramienta:** Antigravity CLI, trabajando por fases en la rama `semana6-revision`.

**Prompt (extractos textuales):** "Cada hallazgo de IA debe verificarse en el código antes de ir al informe"; "NUNCA se modifica una prueba existente para que pase"; evaluar el uso de `x-goog-api-key`.

| Hallazgo de la IA | ¿Real o falso positivo? | Cómo lo verifiqué |
|---|---|---|
| H-01: fallback JWT | Real | Diff `ade50ff`, configuración actual y plantilla vacía. |
| H-02: CORS abierto | Real | Diff `e6a41d6` y política actual en `main.py`. |
| H-03: errores de Gemini | Real | Diff `9ef3d8a` y dos pruebas nuevas de timeout y conexión. |
| H-04: falta de pruebas de abuso | Real | Cuatro pruebas nuevas y suite backend. |
| H-05: rango abierto de dependencia | Real | `requirements.txt` fijado y auditoría limpia. |
| H-06: clave en URL | Real | Prueba nueva y [documentación oficial de Gemini](https://ai.google.dev/gemini-api/docs/api-key), que muestra `x-goog-api-key` en REST. |
| B008, S101, S105/S106, E501 | Falsos positivos en el contexto indicado | Usos de FastAPI, pytest, OAuth2 y docstrings originales revisados. |

**Lo que la IA no encontró:** H-07, pruebas no aisladas. Antigravity reportó las pruebas en verde, pero al ejecutar `pytest` dos veces seguidas la segunda falla (170 % en vez de 85 %), porque las pruebas escriben en la base compartida `backend/gastos.db` y los gastos se acumulan. Lo detecté yo al volver a ejecutar la suite.

## 4. Pendientes

| Pendiente | Por qué no se corrigió todavía | Plan |
|---|---|---|
| H-07: base de datos de pruebas compartida | Una segunda ejecución acumula gastos y falla el porcentaje. No se modificó el `85 %` de la prueba para ocultarlo; el README advierte borrar `backend/gastos.db` antes de `pytest`. | Crear un `conftest.py` con base temporal por ejecución, sin cambiar ninguna aserción. |
| Frontend: `npm run test:unit` | Compila y reporta 2 pruebas aprobadas, pero termina con error asíncrono `NG04002` en `src/app/home/home.page.spec.ts`. No se modificó esa prueba existente. | Revisar la navegación a `/login` en el entorno de pruebas. |

**Claves expuestas:** ver sección 1. No se detectaron claves reales de Gemini/OpenAI; el fallback JWT de H-01 se eliminó.

## 5. Actualización de estado — 19/11/2026

Los pendientes anteriores describen el estado de la revisión original; se
actualizan aquí sin alterar el registro histórico:

- **H-07 resuelto:** `backend/tests/conftest.py` configura una base SQLite
  temporal para la suite. Verificación actual: `python -m pytest -q`, 19/19
  pruebas aprobadas.
- **Prueba unitaria de HomePage resuelta:** `npm run test:unit -- --watch=false`
  aprobó 5/5 pruebas.
- **Flujos de navegador:** `npm run test:e2e` aprobó 3/3 pruebas, incluyendo el
  guardado offline en IndexedDB y la persistencia del tema.
- **Build y lint focalizado:** `npm run build` y ESLint sobre los archivos
  ajustados finalizaron correctamente. Angular muestra avisos de navegadores
  antiguos en Browserslist; pytest muestra dos avisos deprecados de Starlette.