# Informe final del proyecto integrador

Proyecto: Aplicación de control de gastos personales con escáner de facturas  
Estudiante: Yeison Edrey Rodriguez Hernandez  
Repositorio: [App_control_de_gastos_personales](https://github.com/edrey-dot/App_control_de_gastos_personales.git)  
Fecha: 2026-11-26  
Curso: (SOF) 3. SEMINARIO EN INTELIGENCIA ARTIFICIAL APLICADA AL CICLO DE VIDA DEL SOFTWARE  
Docente: Jorge Luis Trujillo Artunduaga (Fundación Escuela Tecnológica de Neiva - FET)  
Ejecución CI: [GitHub Actions CI #2 — Aprobado](https://github.com/edrey-dot/App_control_de_gastos_personales/actions/runs/45858304740)

## 1. Resumen

El proyecto es una aplicación móvil/web en Ionic/Angular con API REST en FastAPI para registrar gastos mediante el escaneo de recibos, definir topes mensuales por categoría y consultar resúmenes; usa SQLite por defecto en desarrollo. La lectura admite modo simulado (mock) y proveedores externos opcionales (Gemini API u OpenAI), y presenta una vista previa para que la persona confirme o corrija los datos antes de guardar. El trabajo abarcó fundamentos, requisitos, diseño, código, seguridad, pruebas y operación, con entregas de Semanas 1–4 en la carpeta padre externa a `App_gastos` y evidencia técnica posterior en el repositorio. La implementación adoptó servidor propio (Ionic/Angular + FastAPI), ajustando la decisión inicial del ADR-001 de conexión directa a IA para proteger claves y filtrar datos sensibles. Según los registros, el backend aprobó 35 pruebas con 85 % de cobertura; el frontend aprobó 18 pruebas unitarias, 7 E2E, `npm run lint` y `build`. GitHub Actions CI #2 también quedó aprobado en `main` el 26/11/2026 ([ejecución](https://github.com/edrey-dot/App_control_de_gastos_personales/actions/runs/45858304740)). Se creó [.dockerignore](./.dockerignore), pero el Dockerfile se pospuso por el fin de vida de Python 3.10; quedan pendientes decisiones y verificaciones antes de producción.

## 2. Problema y usuario

Según la propuesta de Semana 2 y el documento de requisitos de Semana 3 (archivos PDF en la carpeta padre externa a `App_gastos`), registrar gastos diarios manualmente es tedioso y repetitivo: las personas olvidan compras pequeñas o pierden tiquetes y al final del mes desconocen en qué gastaron su dinero. El usuario objetivo intenta controlar sus gastos personales y se desplaza habitualmente sin datos móviles («La mayoría del tiempo no tengo datos»), por lo que necesita fotografiar recibos sin conexión y procesarlos al recuperar señal.

El levantamiento de requisitos se realizó mediante una entrevista de 12 preguntas con cliente simulado, el 24/10/2026, durante 5 minutos. El propio estudiante actuó como usuario final autorizado y se usaron ejemplos ficticios, sin datos de terceros. Antes del sistema, llevaba sus gastos en Excel de forma desordenada, pasaba semanas sin registrar compras, olvidaba gastos en efectivo y perdía recibos. De la entrevista surgieron 11 necesidades con cita textual (N-01 a N-11), 9 historias (HU-01 a HU-09: 5 Must, 3 Should, 1 Could) y 5 requisitos no funcionales (RNF-01 a RNF-05); se excluyeron redes sociales y conexión a claves bancarias (N-11). La propuesta y la entrevista están documentadas en las entregas externas de Semanas 2 y 3 listadas en Anexos.

## 3. La IA en el ciclo de vida

| Módulo y fase | Qué hiciste con IA | Herramienta | Evidencia (enlace) | Cómo verificaste |
|---|---|---|---|---|
| **1. Fundamentos (Semanas 1–2)** | Laboratorio comparativo de función Python para validar correos con 3 pruebas; apoyo conceptual para mapa en Canva sobre IA en el ciclo de vida; banco de 10 prompts con plantilla reutilizable y redacción/síntesis de la propuesta del proyecto final. | Claude y ChatGPT (Semana 1, eligió Claude); Canva (mapa); Gemini y Claude (Semana 2). | Entregas externas: `Rodriguez_Hernandez_Yeison_Edrey_s1_laboratorio.pdf` y `Rodriguez_Hernandez_Yeison_Edrey_S2_Banco.pdf`. | Ejecución en terminal de los scripts de validación; contraste de conceptos con lecturas de Semana 1 reescribiendo definiciones; evaluación de calidad (1–5) e iteración de prompts (ej. prompts 1→2 y 3→4). |
| **2. Requisitos (Semana 3 y consolidación Semanas 7–8)** | Guion de entrevista de 12 preguntas; extracción de necesidades con citas (N-01 a N-11), 9 historias con Gherkin, 5 RNF (ISO/IEC 25010), priorización MoSCoW (5 Must = 55,6 %), matriz de trazabilidad y preguntas pendientes (P-01 a P-07). | Claude (proyecto propio Semana 3); ChatGPT (taller Tienda La Esquina); asistente no especificado nominalmente en Semanas 7–8. | Entrega externa: `Rodriguez_Hernandez_Yeison_Edrey_S3_Requisitos_banco_promts.pdf`; repo: [criterios_aceptacion.md](./criterios_aceptacion.md), [registro_pruebas.md](./registro_pruebas.md), [bitacora_ia.md](./bitacora_ia.md). | Revisión cita por cita contra la transcripción del 24/10/2026; chequeo INVEST y MoSCoW; detección de 3 requisitos inventados, 3 ambigüedades, 1 contradicción y 3 omisiones; confirmación de reglas límite el 26/11/2026. |
| **3. Diseño (Semana 4 y ajustes de implementación)** | Atributos de calidad con pesos (Seguridad 5, Eficiencia 4, Fiabilidad 4, Adecuación 3), 3 alternativas y matriz ponderada, diagramas C4 en Mermaid, modelo ER (USUARIO, CATEGORIA, GASTO, TOPE_MENSUAL), diseño de 5 endpoints REST y ADR-001/ADR-002. Decisiones posteriores de IndexedDB, SQLite y temas. | Claude (prompts 7.1–7.5 en Semana 4); herramienta de ajustes posteriores en [DECISIONES.md](./DECISIONES.md) no especificada por entrada. | Entrega externa: `Rodriguez_Hernandez_Yeison_Edrey_S4_Diseno.pdf` e `INSTRUCCIONES.txt`; repo: [DECISIONES.md](./DECISIONES.md). | Revisión de pesos contra RNF-01 a RNF-05, corrección de cálculo de la matriz (B: 63/80), incorporación propia de USUARIO (ADR-002) y adopción de arquitectura con servidor (`INSTRUCCIONES.txt`). |
| **4. Código (Semanas 5–6 y ajustes Semana 8)** | Contrato y TDD de HU-02 (`validar_fecha_gasto`); implementación base de FastAPI e Ionic/Angular; corrección de hallazgos H-01 a H-06 (clave JWT obligatoria, CORS limitado, timeouts en IA, clave Gemini solo en header, versiones fijadas) y ajuste de mensajes/alertas. | Antigravity CLI (Semanas 5–6); Copilot SDK en VS Code (revisión posterior y Semana 8). | [bitacora_ia.md](./bitacora_ia.md), [revision_seguridad.md](./revision_seguridad.md), [registro_pruebas.md](./registro_pruebas.md); commits en `main` (ej. `35e3f1f`, `ade50ff`, `e6a41d6`, `9ef3d8a`, `db9f6d3`, `91c70e5`, `dd03107`). | Pruebas API/regresión (`pytest`), Ruff 0.17.5, pip-audit 2.10.1 y lectura directa de diffs. [Historial de commits](https://github.com/edrey-dot/App_control_de_gastos_personales/commits/main). |
| **5. Pruebas (Semanas 7–8)** | Diseño de particiones, límites y tabla de decisión (HU-08); pruebas parametrizadas con fixture sintético (`contexto_sintetico`), pruebas de abuso (H-04), auditoría de sensibilidad con 3 mutaciones temporales y formateo de los 21 archivos señalados por Prettier. | Asistente de Semanas 7–8 (herramienta específica no registrada en entradas 6–8); Copilot SDK en VS Code para cierre de frontend/Prettier. | [registro_pruebas.md](./registro_pruebas.md), [criterios_aceptacion.md](./criterios_aceptacion.md), `backend/tests/test_semana7.py`, `backend/tests/test_seguridad_abuso.py`. | Backend: 35 pruebas aprobadas y 85 % de cobertura; 3 mutaciones detectadas. Frontend (26/11/2026): 18 unitarias, 7 E2E, `npm run lint` y build aprobados localmente y en CI. |
| **6. Operación (Semana 9)** | Creación de pipeline CI para `push`/`pull_request` y `.dockerignore`; evaluación de Dockerfile; documentación de recomendaciones de liveness/readiness, logs sanitizados, métricas/alertas y respaldos. | Copilot SDK en VS Code. | [.github/workflows/ci.yml](./.github/workflows/ci.yml), [.dockerignore](./.dockerignore), [docs/revision_configuracion.md](./docs/revision_configuracion.md); ejecución CI #2, run 45858304740. | CI aprobado en GitHub Actions ([ejecución](https://github.com/edrey-dot/App_control_de_gastos_personales/actions/runs/45858304740)): Backend checks (49 s) y Frontend checks (2 min 10 s) en verde. Dockerfile pospuesto por EOL de Python 3.10. |

## 4. Verificación: lo que la IA hizo mal y cómo lo encontraste

### Caso 1: Requisitos inventados, ambigüedades y contradicciones (Semana 3)

- **Fase:** Requisitos (Módulo 2).
- **Qué propuso la IA:** Al extraer necesidades e historias de la entrevista simulada (Prompt 1.2 con Claude), introdujo elementos sin respaldo en la transcripción y términos imprecisos.
- **Qué estaba mal:** Se detectaron 3 requisitos inventados (categoría obligatoria al guardar sin cita, cuenta de usuario y estado «Por confirmar»), además de ideas sin respaldo como gasto sin recibo y alerta sobre el sueldo; 3 ambigüedades (ej. «casi de inmediato», «gráficos súper sencillos»), 1 contradicción (procesar «automáticamente» sin internet frente a exigir vista previa antes de guardar) y 3 omisiones sobre gastos en efectivo sin recibo.
- **Cómo lo detectaste:** Contrasté cada cita y criterio contra la transcripción original y verifiqué la matriz frente a INVEST y MoSCoW.
- **Qué hiciste:** Excluí de los requisitos los elementos sin cita y los pasé a preguntas pendientes (P-01 a P-07); convertí frases vagas en métricas verificables (gráfico de pastel con porcentajes, 5 segundos máximo) y dejé explícitos los supuestos. La cuenta de usuario quedó fuera por falta de respaldo y luego se retomó como decisión propia de diseño (ADR-002, Caso 2). Evidencia: entrega externa `Rodriguez_Hernandez_Yeison_Edrey_S3_Requisitos_banco_promts.pdf` (secciones 7–8 y tabla de defectos).

### Caso 2: Error aritmético, contradicción narrativa y omisión de USUARIO (Semana 4)

- **Fase:** Diseño (Módulo 3).
- **Qué propuso la IA:** En la matriz ponderada (prompts 7.2 y 7.4 con Claude), calculó mal un puntaje de la Alternativa B, redactó una consecuencia contradictoria y generó un modelo de datos inicial solo con GASTO, CATEGORIA y TOPE_MENSUAL.
- **Qué estaba mal:** (1) Calculó 4 × 5 = 25 en lugar de 20 y subvaloró Seguridad en B; (2) afirmó que B perdía velocidad por «pasar por el servidor» aunque B no tenía servidor propio; y (3) omitió USUARIO, necesaria para aislar gastos, gráficos y topes de distintas personas; además incluyó códigos 401 en la API sin historia de origen.
- **Cómo lo detectaste:** Revisé manualmente multiplicaciones y sumas, coherencia entre alternativas y el modelo ER frente a la necesidad de aislar gastos por persona.
- **Qué hiciste:** Corregí los puntajes (B: 63/80), pedí agregar USUARIO y documenté ADR-002 como decisión propia. Posteriormente, `INSTRUCCIONES.txt` resolvió la tensión con RNF-02/RNF-03 adoptando FastAPI. Evidencia: entrega externa `Rodriguez_Hernandez_Yeison_Edrey_S4_Diseno.pdf` (sección 4 y resumen de errores).

### Caso 3: Confundir el mensaje de interfaz con el contrato de API y errores de tildes (Semanas 7–8)

- **Fase:** Código y pruebas de aceptación.
- **Qué propuso la IA:** Que para el texto `abc` en monto, la API devolviera exactamente el mensaje de validación visible en la vista previa; además, el código inicial respondía `numero` y `categoria` sin tilde.
- **Qué estaba mal:** El mensaje exacto para `abc` correspondía a la vista previa de interfaz (FastAPI responde 422 de parseo), y las cadenas sin tilde incumplían el texto literal exigido por HU-03 (número) y HU-04 (categoría).
- **Cómo lo detectaste:** Fallaron las pruebas parametrizadas de aceptación al comparar los mensajes con las aserciones basadas en las historias.
- **Qué hiciste:** Separé las aserciones de API e interfaz sin alterar el criterio de aceptación y corregí las tildes en backend y frontend; después, las pruebas pasaron. Evidencia: [registro_pruebas.md](./registro_pruebas.md) y [criterios_aceptacion.md](./criterios_aceptacion.md). La salida completa de la primera ejecución fallida no se conservó como archivo independiente; la evidencia es el registro en esos documentos.

### Caso 4: Pruebas contaminadas por SQLite compartida y clave Gemini en URL (Semana 6)

- **Fase:** Seguridad y calidad.
- **Qué propuso o no encontró la IA:** En la revisión de seguridad, el agente informó la suite en verde sin advertir que las pruebas escribían sobre `backend/gastos.db` compartida; además, `GeminiReceiptReader` enviaba `self.api_key` en `?key=` junto con el encabezado y `.env.example` conservaba un valor de ejemplo.
- **Qué estaba mal:** Al ejecutar `pytest` dos veces, los gastos se acumulaban y el porcentaje del tope subía a 170 % en vez de 85 %; exponer la clave en `?key=` podía registrarla en logs de red/proxies.
- **Cómo lo detectaste:** Repetí `pytest` comparando con la primera corrida, inspeccioné `receipt_reader.py` y verifiqué la documentación de Gemini sobre `x-goog-api-key`.
- **Qué hiciste:** Registré H-07 y creé `backend/tests/conftest.py` con base SQLite temporal aislada por sesión (suite de 19/19 y luego 35 pruebas); también moví la clave Gemini únicamente al header `x-goog-api-key` ([commit db9f6d3](https://github.com/edrey-dot/App_control_de_gastos_personales/commit/db9f6d3)) y dejé `SECRET_KEY=` vacía en `backend/.env.example` ([commit e981df2](https://github.com/edrey-dot/App_control_de_gastos_personales/commit/e981df2)). Evidencia: [revision_seguridad.md](./revision_seguridad.md), [bitacora_ia.md](./bitacora_ia.md).

### Caso 5: Dockerfile inicial sobre Python 3.10 EOL, Prettier y orden en CI (Semana 9)

- **Fase:** Operación y calidad.
- **Qué propuso la IA:** Inicialmente propuso contenedorizar el backend con Python 3.10 (runtime local) y ubicó la comprobación de formato (`npm run lint`) antes de las pruebas y el build.
- **Qué estaba mal:** Según [PEP 619](https://peps.python.org/pep-0619/), Python 3.10 alcanzó su fin de vida el 2026-10-01, sin soporte de seguridad; además, Prettier reportó 21 archivos fuera de formato, lo que impedía conocer el resultado de pruebas unitarias, E2E y compilación en esa ejecución.
- **Cómo lo detectaste:** Contrasté la versión propuesta contra PEP 619, revisé la salida de `npm run lint` y el YAML del workflow.
- **Qué hiciste:** Pospuse el Dockerfile hasta migrar a Python con soporte vigente (manteniendo 3.10 en CI solo como check de compatibilidad), autoricé formatear únicamente esos 21 archivos y moví el check de formato al final del job frontend. Evidencia: [docs/revision_configuracion.md](./docs/revision_configuracion.md) y [.github/workflows/ci.yml](./.github/workflows/ci.yml).

## 5. Estado final del sistema

- **Arquitectura:** Frontend Ionic 9 / Angular 22 (standalone) con cola offline persistente en IndexedDB (Blob), API REST Python/FastAPI con autenticación JWT (bcrypt + PyJWT) y SQLite por defecto (`gastos.db`); lectura de recibos en modo mock, Gemini u OpenAI, configurables solo en backend ([README.md](./README.md), [DECISIONES.md](./DECISIONES.md)).
- **Funcionalidades terminadas:** Estado basado en la priorización MoSCoW de Semana 3 y la implementación en `App_gastos`.

  | Historia / decisión | Prioridad | Alcance y estado observado |
  |---|---|---|
  | **HU-01 Captura y lectura OCR** | **Must** | Implementada (`POST /recibos/lecturas`, `ReceiptService`). Evaluación con 10 recibos reales (precisión ≥ 8/10 y tiempo ≤ 5 s, RNF-01/RNF-05): pendiente ([PREGUNTAS.md](./PREGUNTAS.md)). |
  | **HU-02 Confirmar vista previa / fecha** | **Must** | Implementada y verificada con pruebas automatizadas backend y frontend ([registro_pruebas.md](./registro_pruebas.md)). |
  | **HU-03 Corregir monto a mano** | **Must** | Implementada y verificada en vista previa (restauración de monto previo) y backend (validación > 0). |
  | **HU-04 Elegir categoría** | **Must** | Implementada (`GET /categorias`, semillas Comida/Transporte/Ocio) y verificada. |
  | **HU-09 Privacidad: solo 4 campos** | **Must** | Implementada (`extra="forbid"`, rechazo HTTP 400 de nombre/tarjeta/dirección, imagen en memoria sin persistencia) y verificada en `test_seguridad_abuso.py`. |
  | **HU-05 Fotos sin internet** | **Should** | Implementada con cola IndexedDB (`OfflineQueueService`) y verificada en flujo web E2E ([revision_seguridad.md](./revision_seguridad.md), sec. 5); falta validación Android/iOS nativo ([PREGUNTAS.md](./PREGUNTAS.md)). |
  | **HU-06 Gráfico de pastel mensual** | **Should** | Implementada (`GET /resumenes`, gráfico conic-gradient); [registro_pruebas.md](./registro_pruebas.md) la identifica como zona con menor cobertura de aceptación backend. |
  | **HU-07 Tope mensual** | **Should** | Implementada (`PUT /topes`, `GET /topes`) y verificada. |
  | **HU-08 Alerta de tope (80 %)** | **Could** | Implementada y verificada con regla confirmada (alerta bajo/sobre 80 %, no exactamente en 80 %); formato exacto del mensaje (ej. al 81 %) sin especificación formal. |
  | **ADR-002 Cuentas y perfil** | **Decisión de diseño** | Implementada (`POST /usuarios`, `POST /sesiones`, `/usuarios/me`), ampliada con nombre para mostrar, celular colombiano y foto de perfil hasta 2 MB ([README.md](./README.md), `backend/tests/test_perfil.py`). No proviene de la entrevista ni de las 9 historias; fue una decisión de diseño propia. |

- **Pruebas:** Backend: 35 pruebas `pytest`, 85 % de cobertura global, Ruff sin avisos y pip-audit 2.10.1 sin vulnerabilidades conocidas ([registro_pruebas.md](./registro_pruebas.md), [docs/revision_configuracion.md](./docs/revision_configuracion.md)). Frontend (26/11/2026): `npm run lint` (ESLint, typecheck, Prettier), 18 pruebas unitarias, 7 E2E Playwright y `npm run build` aprobados. GitHub Actions CI #2 aprobó backend y frontend en `main`, commit `dd03107`, duración total 2 min 14 s (Backend checks: 49 s; Frontend checks: 2 min 10 s): [ejecución](https://github.com/edrey-dot/App_control_de_gastos_personales/actions/runs/45858304740). También se registró CI #1 en `semana9-ci-docker-monitoreo`.
- **Pendientes:** Elegir Python con soporte vigente antes de crear Dockerfile; definir URL HTTPS/TLS pública en `src/environments/environment.prod.ts`; decidir entre SQLite o PostgreSQL administrado con migraciones y respaldos (RPO/RTO); implementar endpoints separados de liveness/readiness y métricas; evaluar precisión y tiempo con 10 recibos reales; validar cámara en dispositivos Android/iOS nativos ([PREGUNTAS.md](./PREGUNTAS.md), [docs/revision_configuracion.md](./docs/revision_configuracion.md)).

## 6. Reflexión ética y legal

| Principio | Decisión en mi proyecto | Evidencia |
|---|---|---|
| **Datos personales (Ley 1581 de 2012)** | Los gastos almacenan exclusivamente comercio, fecha, monto y categoría (HU-09, RNF-02), y rechazan campos extra con HTTP 400 (R-03). La cuenta maneja correo, contraseña con bcrypt, nombre para mostrar, celular opcional y foto de perfil ([README.md](./README.md)). Para la entrevista simulada del 24/10/2026, el estudiante dio consentimiento para usar sus respuestas con IA y se utilizaron ejemplos ficticios. Las pruebas usan datos sintéticos y BD temporal. El modo externo envía fotos de recibos al proveedor; no existe en el repo aviso de privacidad ni consentimiento informado formal para el usuario final. Esto no constituye certificación legal. | [README.md](./README.md), [registro_pruebas.md](./registro_pruebas.md), [revision_seguridad.md](./revision_seguridad.md), [PREGUNTAS.md](./PREGUNTAS.md); entrega S3 externa. |
| **Sesgo** | Aún no se ha ejecutado evaluación empírica de sesgo o precisión con 10 recibos reales colombianos (RNF-05 ≥ 8/10 y RNF-01 ≤ 5 s). No se reportan tasas reales de error ni desempeño en producción; la validación queda pendiente. | [PREGUNTAS.md](./PREGUNTAS.md), [README.md](./README.md). |
| **Transparencia** | El [README.md](./README.md) declara el modo simulado o externo (Gemini/OpenAI), que la foto no se almacena en la BD del backend y que la persona revisa los datos antes de guardar. Las decisiones y errores de IA constan en la bitácora y entregas semanales. Falta un aviso visible en la interfaz móvil antes de enviar una foto al proveedor externo. | [README.md](./README.md), [bitacora_ia.md](./bitacora_ia.md), [PREGUNTAS.md](./PREGUNTAS.md). |
| **Responsabilidad** | Aunque la IA extrae campos y asistió en requisitos, diseño, código y pruebas, el sistema exige una vista previa editable antes de persistir el gasto (HU-02, HU-03). El estudiante tomó y verificó decisiones de alcance, arquitectura (ADR-002 y cambio de Alternativa B a servidor), límites de pruebas y posposición del despliegue. | [criterios_aceptacion.md](./criterios_aceptacion.md), [registro_pruebas.md](./registro_pruebas.md); entrega S4 externa. |
| **Propiedad intelectual y política de uso** | El [README.md](./README.md) declara licencia MIT © 2026 Yeison Edrey Rodriguez Hernandez, pero no hay archivo LICENSE independiente ni auditoría formal de compatibilidad de licencias de dependencias o términos comerciales de las APIs de visión. | [README.md](./README.md); archivo LICENSE y política institucional no encontrados en el repo. |

El dilema ético central es equilibrar la utilidad de automatizar la lectura de recibos con visión artificial frente al riesgo de privacidad (N-10) al enviar imágenes reales —que pueden incluir nombre, últimos dígitos de tarjeta o dirección— a proveedores externos (Google u OpenAI). Se implementaron mitigaciones técnicas: descarte inmediato de la imagen en memoria, sin guardarla en servidor ni BD; rechazo HTTP 400 de campos sensibles; claves aisladas en `.env` del backend; y modo mock local. Sin embargo, la falta de aviso de privacidad y consentimiento explícito en la interfaz, además de la falta de definición sobre retención por el proveedor elegido ([PREGUNTAS.md](./PREGUNTAS.md), #3), impide considerar cerrado el dilema legal y de gobernanza antes de producción.

## 7. Aprendizajes

A lo largo de las 10 semanas del seminario —alineado con las OVAs «Tendencias y sustentación» e «IA responsable y gobernanza»— mi rol evolucionó de solicitar fragmentos de código a dirigir y auditar el trabajo asistido por IA en cada fase del ciclo de vida. En las entregas iniciales (Semanas 1–4) comprobé que la IA agiliza guiones, historias Gherkin y diagramas, pero también inventa requisitos sin cita, introduce errores aritméticos y contradicciones en matrices de diseño y omite entidades esenciales como USUARIO; por eso, sus resultados deben verificarse contra fuentes primarias y decisiones propias de negocio.

En las fases técnicas (Semanas 5–9) aprendí que una suite en verde o una cobertura del 85 % no garantizan calidad por sí solas: las pruebas de aceptación detectaron discrepancias de texto (tildes), las mutaciones comprobaron si se detectaban validaciones débiles y repetir `pytest` reveló contaminación de datos en SQLite que la IA había pasado por alto. Validar configuraciones contra fuentes oficiales evitó construir un contenedor sobre Python 3.10 sin soporte y llevó a ordenar correctamente el CI antes de aprobarlo en GitHub Actions. En una próxima iteración establecería desde el inicio la matriz de trazabilidad, fijaría un runtime con soporte vigente, automatizaría la limpieza del entorno de pruebas y distinguiría claramente lo verificado localmente y en CI de lo pendiente en la nube.

## 8. Anexos

- **Bitácora de uso de IA:** [bitacora_ia.md](./bitacora_ia.md).
- **Documentos de cada módulo y evidencias:**
  - **Módulo 1 / Semana 1:** `Rodriguez_Hernandez_Yeison_Edrey_s1_laboratorio.pdf` (carpeta padre externa).
  - **Semana 2:** `Rodriguez_Hernandez_Yeison_Edrey_S2_Banco.pdf` (carpeta padre externa).
  - **Módulo 2 / Semana 3:** `Rodriguez_Hernandez_Yeison_Edrey_S3_Requisitos_banco_promts.pdf` (carpeta padre externa).
  - **Módulo 3 / Semana 4:** `Rodriguez_Hernandez_Yeison_Edrey_S4_Diseno.pdf` e `INSTRUCCIONES.txt` (carpeta padre externa).
  - **Criterios y pruebas (Semanas 7–8):** [criterios_aceptacion.md](./criterios_aceptacion.md), [registro_pruebas.md](./registro_pruebas.md).
  - **Seguridad y decisiones (Semanas 6–8):** [revision_seguridad.md](./revision_seguridad.md), [DECISIONES.md](./DECISIONES.md), [PREGUNTAS.md](./PREGUNTAS.md).
  - **Operación y CI/CD (Semana 9):** [docs/revision_configuracion.md](./docs/revision_configuracion.md), [.github/workflows/ci.yml](./.github/workflows/ci.yml), [.dockerignore](./.dockerignore).
  - **Ejecución CI #2 y commits:** [GitHub Actions](https://github.com/edrey-dot/App_control_de_gastos_personales/actions/runs/45858304740), [historial de `main`](https://github.com/edrey-dot/App_control_de_gastos_personales/commits/main).
  - **Material sobre el ciclo de vida de Python 3.10:** [PEP 619](https://peps.python.org/pep-0619/).

