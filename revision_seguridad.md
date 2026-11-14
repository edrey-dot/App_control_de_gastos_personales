# Revisión de seguridad — Semana 6

**Proyecto:** Control de gastos personales  
**Estudiante:** [COMPLETAR POR MÍ]  
**Fecha:** 2026-11-14  
**Commit revisado:** `35e3f1f`

## 1. Herramientas, criterios y revisión base

Ruff **0.17.5**, reglas **E, F, B, S**: `ruff check .` pasó. `pip-audit`
**2.10.1**: **No known vulnerabilities found**. Las configuraciones Ruff raíz
y backend son idénticas. La suite backend pasó **15/15** con una base temporal
limpia. Se revisaron los cinco controles de la semana:

| Punto | Resultado |
|---|---|
| Inyección | Consultas por ORM SQLAlchemy; no se encontró SQL por concatenación (`backend/app/api/gastos.py:46`). |
| Secretos | `.env` no está versionado; `.env.example` deja `SECRET_KEY=` vacía (`backend/.env.example:2`). |
| Contraseñas | Passlib/bcrypt y mínimo de 8 caracteres (`backend/app/core/security.py:12`, `backend/app/schemas/auth.py:21`). |
| Acceso | Filtros por usuario autenticado; gasto ajeno devuelve 404 (`backend/app/api/gastos.py:129`). |
| Dependencias | 11 requisitos fijados con `==`; auditoría limpia. |

**Claves reales de Gemini/OpenAI expuestas: Ninguna detectada** en el historial
Git revisado. No se halló un archivo `.env`; sin embargo, sí se había versionado
el fallback JWT fijo y predecible de H-01. No sería correcto afirmar que nunca
se subió ningún valor de clave. El fallback y el valor de demostración de la
plantilla se eliminaron.

## 2. Hallazgos y avisos de linter

| Id | Archivo y línea | Problema | OWASP | Severidad | Corrección | Commit |
|---|---|---|---|---|---|---|
| H-01 | `backend/app/core/config.py:10`; `backend/.env.example:2` | Fallback JWT predecible | A02 Cryptographic Failures | Alta | Clave obligatoria; plantilla vacía | `ade50ff`, `e981df2` |
| H-02 | `backend/app/main.py:51` | CORS permisivo | A05 Security Misconfiguration | Media | Orígenes/métodos/encabezados limitados | `e6a41d6` |
| H-03 | `backend/app/services/receipt_reader.py:153` | Timeout y errores de red sin manejo controlado | Sin correspondencia directa; robustez | Media | Manejo controlado y pruebas de regresión | `9ef3d8a`, `2e06162` |
| H-04 | `backend/tests/test_seguridad_abuso.py:14` | Faltaban pruebas de abuso y aislamiento | A01 Broken Access Control (brecha de pruebas) | Media | Cuatro pruebas nuevas | `38fc0e6`, `caaa892` |
| H-05 | `backend/requirements.txt:11` | Dependencia con rango abierto | A06 Vulnerable and Outdated Components | Baja | Versiones exactas; multipart `==0.0.32` | `f0a1122`, `89eaa10` |
| H-06 | `backend/app/services/receipt_reader.py:121` | Clave Gemini en `?key=` | A02 Cryptographic Failures | Baja | Solo `x-goog-api-key`; prueba nueva | `db9f6d3` |
| H-07 | `backend/app/core/config.py:20`; `backend/tests/test_api_endpoints.py:13` | Pruebas acumulan datos en SQLite compartida | No aplica; aislamiento de pruebas | Baja | Pendiente: base temporal por suite | — |

Avisos no corregidos y justificación:

| Regla | Justificación |
|---|---|
| B008 | Falso positivo por `Depends`, `Query` y `File` de FastAPI. |
| S101 | `assert` es el uso esperado en pruebas pytest. |
| S105/S106 | `bearer` es el tipo de token OAuth2, no un secreto. |
| E501 | Dos docstrings originales largos (`tests/test_validaciones.py:54,81`); se conservaron intactos. |

**Refactor sin cambio funcional:** se nombró el umbral `80` como
`UMBRAL_ALERTA_PORCENTAJE` (`backend/app/api/topes.py:14`, commit `7633004`).
La fórmula de porcentaje se repite, pero los endpoints devuelven precisión
distinta; no se extrajo para evitar alterar el comportamiento.

**Verificación personal:** H-01 [COMPLETAR POR MÍ]; H-02 [COMPLETAR POR MÍ];
H-03 [COMPLETAR POR MÍ]; H-04 [COMPLETAR POR MÍ]; H-05 [COMPLETAR POR MÍ];
H-06 [COMPLETAR POR MÍ].

## 3. Revisión con IA

**Prompt (extractos textuales):** “Cada hallazgo de IA debe verificarse en el
código antes de ir al informe”; “NUNCA se modifica una prueba existente para
que pase”; evaluar el uso de `x-goog-api-key`.

| Hallazgo de la IA | Real o falso positivo | Verificación |
|---|---|---|
| H-01: fallback JWT | Real | Diff `ade50ff`, configuración actual y plantilla vacía. |
| H-02: CORS abierto | Real | Diff `e6a41d6` y política actual en `main.py`. |
| H-03: errores de Gemini | Real | Diff `9ef3d8a` y dos pruebas nuevas de timeout/conexión. |
| H-04: falta de pruebas de abuso | Real | Cuatro pruebas nuevas y suite backend. |
| H-05: rango abierto de dependencia | Real | `requirements.txt` fijado y auditoría limpia. |
| H-06: clave en URL | Real | Prueba nueva y [documentación oficial Gemini](https://ai.google.dev/gemini-api/docs/api-key), que muestra `x-goog-api-key` en REST. |
| B008, S101, S105/S106, E501 | Falsos positivos en el contexto indicado | Usos FastAPI, pytest, OAuth2 y docstrings originales revisados. |

**Lo que la IA no encontró:** [COMPLETAR POR MÍ: anotar hallazgos propios o
limitaciones que identifiqué.]

## 4. Pendientes

- **H-07:** base de datos de pruebas compartida; una segunda ejecución puede
  acumular gastos y fallar el porcentaje. No se modificó el `85 %`; README
  advierte borrar `backend/gastos.db` antes de pytest. En base temporal limpia
  pasaron 15 pruebas.
- **Frontend:** `npm run test:unit` compila y reporta 2 pruebas aprobadas, pero
  termina con error asíncrono `NG04002` en `src/app/home/home.page.spec.ts`.
  No se modificó esa prueba existente.
- Completar nombre, verificaciones personales y observaciones propias de la IA.
