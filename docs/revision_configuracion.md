# Revisión de configuración CI/CD y operación

Proyecto: App_gastos

Fecha: 2026-11-26

## 1. Origen y alcance

**Herramienta de IA:** Copilot SDK en Visual Studio Code.

**Solicitud:** revisar CI/CD, contenedores y operación; crear el pipeline, `.dockerignore` y el reporte tras aprobación.

**Aprobación aplicada:** crear CI de compatibilidad con Python 3.10, `.dockerignore` de raíz y este reporte; posponer el `Dockerfile` por el fin de vida de Python 3.10. Después, con autorización, se formatearon únicamente los 21 archivos señalados por Prettier; no se cambiaron intencionalmente reglas ni comportamiento de aplicación.

El diagnóstico partió del repositorio y de la plantilla `revision_configuracion.md` proporcionada por el usuario. No se leyeron los valores de `backend/.env` ni se incluyeron secretos. El proyecto documenta Python 3.10 y la API usa SQLite por defecto. La fuente oficial [PEP 619](https://peps.python.org/pep-0619/) confirma que Python 3.10 terminó su ciclo de vida el 2026-10-01; por ello, el job de CI solo verifica compatibilidad con el runtime actual y no certifica que sea apropiado para producción.

## 2. Hallazgos y cambios

| Archivo y línea | Hallazgo / problema | Riesgo | Cambio o estado |
|---|---|---|---|
| `.github/workflows/ci.yml` (nuevo) | El repositorio no tenía workflow. | No se ejecutaban automáticamente pruebas ni verificaciones en cambios de GitHub. | Añadido workflow para push y pull request, permisos `contents: read`, acciones fijadas por SHA, y jobs backend/frontend. El backend corre Ruff, `pip-audit` y pytest; el frontend ejecuta ESLint, typecheck, pruebas unitarias, Playwright, build y Prettier. No requiere secretos de producción. |
| `.dockerignore` (nuevo, raíz) | No había exclusiones para contexto Docker. | Riesgo de incluir `.env`, bases locales, dependencias, caches o resultados de pruebas si se construye con el contexto raíz. | Añadidas exclusiones de configuración sensible, datos SQLite, metadatos Git, dependencias, caches y artefactos de pruebas. |
| `backend/Dockerfile` (ausente) | La aplicación no tiene imagen. | Python 3.10 llegó a fin de vida; crear una imagen de producción sobre esa base presentaría un runtime sin soporte de seguridad. SQLite también necesita persistencia y respaldo fuera del contenedor. | **Pospuesto por decisión del usuario.** No se construyó ni verificó ninguna imagen. Revisar el runtime mantenido y la persistencia/respaldos antes de definir el Dockerfile. |
| `src/environments/environment.prod.ts` | La URL documentada de API es `http://localhost:8000`; TLS/servidor de producción no forman parte del repo. | El frontend desplegado no apuntará automáticamente a una API remota segura. | Sin cambios. Configurar la URL HTTPS real cuando se conozca el entorno de despliegue. |
| `backend/app/main.py`, `backend/app/api/recibos.py` | La ruta `/` informa estado estático; solo se encontró un warning explícito de aplicación para errores del proveedor de recibos. | No se verifica readiness de base de datos ni se dispone de observabilidad operativa completa. | Recomendación pendiente: separar liveness/readiness, estructurar logs con identificador de solicitud y evitar datos personales, imágenes, tokens o claves. No se modificó su comportamiento; los únicos cambios de aplicación en este alcance fueron de formato y están descritos arriba. |
| SQLite / respaldos | No se encontró job de respaldo ni procedimiento de restauración. | Riesgo de pérdida de datos o respaldo no consistente durante escrituras. | Recomendación pendiente: definir RPO/RTO/retención, usar respaldo consistente de SQLite, guardar copia cifrada fuera del host y ensayar restauración. No se asignaron umbrales no confirmados. |

## 3. Revisión con herramientas

| Herramienta | Avisos | ¿Coinciden con los hallazgos? | ¿Qué no encuentra por sí sola? |
|---|---|---|---|
| `actionlint` | No ejecutado: no está instalado en el entorno de trabajo. | No se puede afirmar resultado. | Requiere revisión adicional de privilegios efectivos, confianza en acciones de terceros, filtración de secretos, calidad de oráculos de pruebas, protección de ramas y ejecución real en GitHub. |
| `hadolint` | No ejecutado: no está instalado y no se creó Dockerfile. | No se puede afirmar resultado. | No demuestra persistencia/restauración de SQLite, seguridad en runtime, estado de CVE de la imagen, ausencia de secretos en historial ni comportamiento bajo carga. |

## 4. Operación, monitoreo y alertas propuestas

No se encontró configuración de métricas o alertas. Las siguientes son propuestas, no instrumentación ni resultados existentes:

- Medir disponibilidad/readiness, errores HTTP 5xx y latencia; definir umbrales después de observar tráfico y acordar objetivos de servicio.
- Vigilar espacio disponible, errores de bloqueo/escritura SQLite y reinicios del proceso.
- Alertar por fallo o antigüedad del último respaldo; probar restauraciones periódicamente y programar la operación según los objetivos acordados y la carga observada.
- Mantener logs sin contenido de recibos, claves, tokens ni datos personales; revisar la sanitización de mensajes externos.
- Mantener el despliegue del frontend y API separado salvo que la plataforma elegida requiera contenedores para ambos.

No se propone monitoreo de modelos, drift ni métricas MLOps.

## 5. Verificación

- **Backend local:** Ruff pasó; `pip-audit` no encontró vulnerabilidades conocidas; pytest: 35 pasaron.
- **Frontend local:** ESLint y typecheck pasaron; pruebas unitarias: 18 pasaron; Playwright: 7 pasaron; build terminó correctamente.
- **Formato frontend:** la primera comprobación encontró 21 archivos fuera del formato esperado. Tras autorización del usuario, se ejecutó Prettier únicamente sobre esos 21 archivos; después `npm run lint` pasó, incluyendo ESLint, typecheck y Prettier. El workflow ejecuta Prettier al final para que el resto de verificaciones también se ejecute.
- **Avisos no bloqueantes observados:** Angular reportó navegadores antiguos configurados en Browserslist que no están soportados por la versión instalada. Las pruebas y el build terminaron correctamente.
- `actionlint`, `hadolint` y Docker no están instalados en este entorno; no se ejecutaron validaciones de esas herramientas ni construcción de imagen.

- [ ] El pipeline se ejecutó en GitHub y terminó en verde.
- [ ] Se hizo fallar una prueba intencionalmente y el pipeline terminó en rojo.
- [ ] Se construyó una imagen Docker. **Pendiente:** Dockerfile pospuesto.
- [ ] Se auditó el historial de Git en busca de claves; no se realizó esta auditoría.
- [ ] Se probó una restauración de respaldo.
- [ ] Se verificó readiness contra una base de datos en el entorno de despliegue.

La creación del workflow y las pruebas locales no equivalen a una ejecución en GitHub. El estado del workflow en GitHub continúa pendiente. No se debe afirmar que el pipeline está verde antes de una ejecución real.
