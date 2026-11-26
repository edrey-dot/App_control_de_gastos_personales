# Registro de pruebas - Semana 7

## 1. Funciones seleccionadas y reglas de negocio

### Fuente de los oráculos

Basé los resultados esperados de esta sección exclusivamente en los criterios de aceptación de las historias de usuario **HU-02, HU-03, HU-04, HU-07 y HU-08**, sin deducirlos de la ejecución previa del código. Los nombres de las funciones indican los puntos exactos donde probé cada regla, entendiendo que la implementación inicial no define el comportamiento esperado.

| Historia y función seleccionada | Regla y resultado esperado según la historia |
| --- | --- |
| HU-02 — `validar_fecha_gasto` | Al guardar, una fecha pasada como 15/10/2026 con hoy 24/10/2026 permite guardar el gasto. Una fecha futura como 30/12/2026 con hoy 24/10/2026 debe impedir el guardado y mostrar exactamente `La fecha no puede ser posterior a hoy`. La marca roja corresponde a la vista previa y no la verifico mediante prueba unitaria del backend. |
| HU-03 — `GastoCreate.validar_monto` | Al corregir el monto leído de $58.000 a 85000, la vista previa debe mostrar $85.000 sin volver a tomar la foto. Si se escribe `abc` o `0`, debe mostrar exactamente `El monto debe ser un número mayor a 0` y conservar el valor anterior. La conservación del valor anterior corresponde a la interfaz; en las pruebas `pytest` del backend verifico únicamente la validación del dato recibido. |
| HU-04 — `GastoCreate.validar_categoria` | Elegir «Comida» y guardar debe dejar el gasto en esa categoría. Si no se elige categoría, debe mostrar exactamente `Elige una categoría` y no guardar el gasto. |
| HU-07 — `TopeCreate.validar_monto_tope` | Definir un tope de $400.000 para «Comida» en octubre de 2026 debe guardarlo y mostrar `Comida: $0 de $400.000`. Un tope de -$50.000 o $0 debe impedir el guardado y mostrar exactamente `El tope debe ser mayor a $0`. |
| HU-08 — `listar_topes` | Con un tope de $400.000 para «Comida» y un gasto mensual acumulado de $325.000, debe producir la alerta `Llevas el 81 % de tu tope en Comida`. Para una categoría sin tope no debe aparecer alerta y la interfaz debe mostrar `Sin tope definido`. La regla combina la existencia del tope y el gasto acumulado respecto de ese tope; el texto de la interfaz no lo compruebo desde la API. |

### Reglas candidatas para la tabla de decisión

Seleccioné **HU-08** para construir la tabla de decisión, evaluando si hay tope para la categoría/período y el gasto acumulado respecto del 80 %. El 26/11/2026, el usuario confirmó que una fecha igual a hoy es válida y que HU-08 debe alertar por debajo y por encima del 80 %, pero no exactamente en 80 %.

### Ambigüedades y discrepancias pendientes

- HU-08 especifica el mensaje del caso de $325.000 sobre $400.000 (81 %), pero no define cómo mostrar porcentajes distintos a ese ejemplo.
- La regla confirmada para HU-08 es no monotónica: hay alerta por debajo del 80 %, no hay alerta exactamente en 80 % y hay alerta por encima del 80 %. La alerta también se activa con gasto de $0 porque es menor al 80 %.
- El mensaje de HU-03 incluye «número» y el de HU-04 «categoría» con tilde. Mis primeras pruebas detectaron que la implementación usaba las versiones sin tilde. Corregí los mensajes tanto en el backend como en la interfaz para cumplir estrictamente el texto de la historia sin alterar el oráculo.
- HU-03 y HU-08 incluyen comportamientos de interfaz (conservar el monto anterior y mostrar «Sin tope definido») que no se pueden afirmar con pruebas unitarias del backend, por lo que no añadí comprobaciones artificiales para ellos.

### Auditoría previa de expectativas

- **Particiones:** Representé en las tablas todas las particiones explícitas válidas e inválidas; los grupos sin oráculo quedaron marcados como pendientes.
- **Límites:** La fecha igual a hoy y los dos bordes de HU-08 se incorporaron tras confirmación explícita del usuario.
- **Origen del resultado esperado:** Vinculé cada resultado a una HU o a la aclaración del usuario, nunca a la ejecución previa del código.
- **Ambigüedades:** Sigue pendiente únicamente el formato del mensaje de alerta para porcentajes distintos del 81 % descrito.
- **Reglas inventadas:** No añadí resultados para los escenarios que las historias no especifican.

## 2. Tablas de casos de prueba

### Particiones de equivalencia

Los casos describen el oráculo funcional. Cuando el criterio corresponde a la interfaz, conservé la fila como requisito documental sin convertirla en una aserción de `pytest` en el backend.

| ID | Función / historia | Partición y entrada | Resultado esperado según la historia | Aplicación |
| --- | --- | --- | --- | --- |
| F02-01 | `validar_fecha_gasto` / HU-02 | Fecha pasada: 15/10/2026; hoy: 24/10/2026 | El gasto queda guardado y aparece el 15/10/2026 por $85.000. | Verifico con `pytest` la validación del backend; la aparición en lista corresponde a integración/UI. |
| F02-02 | `validar_fecha_gasto` / HU-02 | Fecha futura: 30/12/2026; hoy: 24/10/2026 | No se guarda y se muestra `La fecha no puede ser posterior a hoy`. | Verifico rechazo y mensaje en backend; el color rojo pertenece a la interfaz. |
| F03-01 | `GastoCreate.validar_monto` / HU-03 | Monto válido corregido: 85000 | La vista previa muestra $85.000 y no se toma otra foto. | Verifico con `pytest` que el backend acepta el monto; la vista previa y la foto son de interfaz. |
| F03-02 | `GastoCreate.validar_monto` / HU-03 | Cero: `0` | Se muestra `El monto debe ser un número mayor a 0` y se conserva el valor anterior. | Verifico rechazo y mensaje; conservar el valor es de interfaz. |
| F03-03 | `GastoCreate.validar_monto` / HU-03 | Texto no numérico: `abc` | Se muestra `El monto debe ser un número mayor a 0` y se conserva el valor anterior. | Verifico rechazo; mensaje y conservación pertenecen a la interfaz. |
| F04-01 | `GastoCreate.validar_categoria` / HU-04 | Categoría elegida: «Comida» | El gasto se guarda en «Comida». | Verificado mediante API con datos sintéticos. |
| F04-02 | `GastoCreate.validar_categoria` / HU-04 | Categoría ausente | No se guarda y se muestra `Elige una categoría`. | Verificado mediante API comparando el mensaje exacto. |
| F07-01 | `TopeCreate.validar_monto_tope` / HU-07 | Tope positivo: $400.000 para «Comida», octubre de 2026 | Se guarda y muestra `Comida: $0 de $400.000`. | Verificado mediante API. |
| F07-02 | `TopeCreate.validar_monto_tope` / HU-07 | Tope negativo: -$50.000 | No se guarda y se muestra `El tope debe ser mayor a $0`. | Verificado mediante API comparando el mensaje exacto. |
| F07-03 | `TopeCreate.validar_monto_tope` / HU-07 | Tope cero: $0 | No se guarda y se muestra `El tope debe ser mayor a $0`. | Verificado mediante API comparando el mensaje exacto. |
| F08-01 | `listar_topes` / HU-08 | Tope definido: $400.000; acumulado: $325.000 (81 % según la historia) | Se muestra `Llevas el 81 % de tu tope en Comida`. | Verifico el indicador y mensaje de alerta desde la API. |
| F08-02 | `listar_topes` / HU-08 | Sin tope para «Ocio»; gasto de $50.000 | No aparece alerta; la interfaz muestra `Sin tope definido`. | Verifico ausencia de alerta en backend; el texto de interfaz queda fuera de `pytest` backend. |

### Valores límite

| Regla | Borde identificado en la historia | Resultado | Estado |
| --- | --- | --- | --- |
| Fecha HU-02 | Día siguiente a hoy: 25/10/2026, con hoy 24/10/2026 | Es una fecha futura; debe rechazarse como la fecha futura del escenario 2. | Caso límite que propuse a partir de la partición explícita «fecha futura». |
| Fecha HU-02 | Fecha igual a hoy: 24/10/2026 | La fecha es válida y se conserva. | Confirmado por el usuario el 26/11/2026; cubierto por `test_hu02_limite_fecha_igual_a_hoy_es_valida`. |
| Monto HU-03 | $0 | Rechazado con el mensaje especificado. | Oráculo explícito. |
| Monto HU-03 | Primer monto positivo representable | La historia no especifica unidad o precisión monetaria mínima. | Pendiente; no inventé una cantidad. |
| Categoría HU-04 | Categoría ausente frente a «Comida» seleccionada | Ausente: rechazo; seleccionada: guardado. | Particiones explícitas; no hay otro límite cuantitativo. |
| Tope HU-07 | $0 y -$50.000 | Ambos rechazados con el mensaje especificado. | Oráculo explícito. |
| Tope HU-07 | Primer tope positivo representable | La historia no especifica unidad o precisión monetaria mínima. | Pendiente; no inventé una cantidad. |
| Alerta HU-08 | Exactamente 80 %: $320.000 de $400.000 | No debe generar alerta. | Confirmado por el usuario el 26/11/2026; cubierto por pruebas backend y frontend. |
| Alerta HU-08 | Por debajo de 80 %: $300.000 de $400.000 (75 %) | Debe generar alerta; el formato del mensaje no está especificado. | Confirmado por el usuario el 26/11/2026; cubierto por prueba backend. |

### Tabla de decisión — alerta HU-08

Evalué las condiciones «hay un tope definido para la categoría/mes» y «el gasto mensual respecto del tope». Las fronteras se incorporaron según la aclaración explícita del usuario del 26/11/2026.

| Regla | ¿Hay tope definido? | ¿Alcanza el umbral? | ¿Alerta? | Resultado esperado | Origen |
| --- | --- | --- | --- | --- | --- |
| D08-1 | Sí | Sí: $325.000 de $400.000 (81 % según HU-08) | Sí | `Llevas el 81 % de tu tope en Comida` | HU-08, escenario 1 |
| D08-2 | No | No aplica: gasto de $50.000 en «Ocio» | No | No aparece alerta; la interfaz indica `Sin tope definido` | HU-08, escenario 2 |
| D08-3 | Sí | Exacto: $320.000 de $400.000 (80 %) | No | No se muestra alerta | Aclaración confirmada por el usuario |
| D08-4 | Sí | Menor: $300.000 de $400.000 (75 %) | Sí | Se muestra una alerta; texto específico pendiente | Aclaración confirmada por el usuario |

### Revisión de los casos diseñados

1. **Particiones:** Incluí las entradas válidas e inválidas que aparecen explícitamente en las historias; señalé como pendientes los grupos no especificados.
2. **Límites:** Anoté cero, el día siguiente y los bordes confirmados; siguen abiertos los valores mínimos positivos.
3. **Origen del esperado:** Vinculé cada resultado esperado a una HU o a la aclaración explícita del usuario, nunca a la ejecución previa del código.
4. **Ambigüedades:** Las mantuve identificadas arriba sin convertirlas en expectativas de prueba.
5. **Reglas inventadas:** No asigné resultados a las filas pendientes ni extendí el ejemplo de porcentaje a otros formatos.

### Auditoría de las pruebas generadas

| Casos | Prueba parametrizada | ¿El esperado viene de HU? | ¿Detecta una rotura de la regla? | ¿Aporta cobertura distinta? | Decisión |
| --- | --- | --- | --- | --- | --- |
| F02-01, F02-02 | `test_hu02_reglas_de_fecha_de_las_historias` | Sí, HU-02 escenarios 1 y 2 | Sí: comprueba que la fecha pasada se acepta y que la futura se rechaza con el mensaje exacto. | Sí: cubre las particiones válida e inválida. | Conservada. |
| F02-03 | `test_hu02_limite_fecha_igual_a_hoy_es_valida` | Sí, aclaración del usuario del 26/11/2026 | Sí: falla si se rechaza la fecha igual a hoy. | Sí: cubre la frontera confirmada. | Conservada e incorporada a los criterios automatizables. |
| F03-01 | `test_hu03_valida_monto_al_guardar[85000]` | Sí, HU-03 escenario 1 | Sí: falla si el monto corregido deja de aceptarse o cambia de valor. | Sí: cubre una entrada numérica válida. | Conservada; utilicé `pytest.approx` para el valor decimal. |
| F03-02 | `test_hu03_valida_monto_al_guardar[0]` | Sí, HU-03 escenario 2 | Sí: falla si cero deja de rechazarse o cambia el mensaje exigido. | Sí: cubre el borde inválido cero. | Conservada; resolví el fallo inicial corrigiendo el mensaje fuente, no el esperado. |
| F03-03 | `test_hu03_valida_monto_al_guardar[abc]` | Sí, HU-03 escenario 2 | Sí: falla si un monto no numérico se acepta. | Sí: distingue texto no numérico del cero numérico. | Conservada. La prueba de backend no afirma el mensaje de interfaz ni que se conserve el valor previo. |
| F04-01, F04-02 | `test_hu04_categoria_requerida` | Sí, HU-04 escenarios 1 y 2 | Sí: verifica el guardado con «Comida» y el rechazo, mensaje y no persistencia si falta categoría. | Sí: cubre las particiones con y sin categoría. | Conservada; resolví el fallo inicial corrigiendo el mensaje fuente, no el esperado. |
| F07-01, F07-02, F07-03 | `test_hu07_valida_tope_mensual` | Sí, HU-07 escenarios 1 y 2 | Sí: comprueba tope positivo, rechazo de negativo/cero y que un rechazo no persista. | Sí: negativo y cero cubren una entrada inválida y el límite cero. | Conservada; utilicé `pytest.approx` en los montos decimales. |
| F08-01, F08-02 | `test_hu08_alerta_depende_de_tope_y_gasto` | Sí, HU-08 escenarios 1 y 2 | Sí: detecta la ausencia de alerta con el caso 81 % o la aparición de un tope/alerta para categoría sin tope. | Sí: ejercita las dos combinaciones definidas de la tabla de decisión. | Conservada. La etiqueta de interfaz «Sin tope definido» no se afirma desde `pytest` backend. |
| F08-03, F08-04 | `test_hu08_alerta_depende_de_tope_y_gasto` | Sí, aclaración del usuario del 26/11/2026 | Sí: detecta alerta al 75 % y ausencia de alerta al 80 % exacto. | Sí: ejercita ambos límites confirmados. | Añadidas; no se fija el texto para el 75 % porque no está especificado. |

#### Pruebas corregidas o descartadas

- Los primeros resultados de **F03-02** y **F04-02** fallaron porque las respuestas del sistema contenían `numero` y `categoria` sin tilde. Mantuve los valores esperados escritos en HU-03/HU-04 y corregí los mensajes correspondientes tanto en el backend como en la interfaz; tras el cambio, ambas pruebas pasaron.
- Actualicé las dos aserciones previas en `test_api_endpoints.py` que esperaban los mensajes sin tilde para alinearlas con las historias.
- No descarté ninguna de las pruebas que generé esta semana.
- La prueba de fecha igual a hoy se mantuvo fuera de los casos nuevos hasta que el usuario confirmó el 26/11/2026 que esa fecha es válida; desde entonces se cuenta como criterio automatizable.

### Actualización Semana 8 — 26/11/2026

- Se añadieron pasos Dado/Cuando/Entonces y aserciones de estado/historial para los casos automatizables HU-02, HU-03, HU-04, HU-07 y HU-08.
- Se verificaron desde la interfaz la fecha futura en rojo, la corrección del monto sin releer el recibo, la restauración del monto anterior y los mensajes/estados de alertas cubiertos por criterios confirmados.
- El usuario confirmó una regla HU-08 no monotónica: alertar por debajo y por encima del 80 %, pero no exactamente en 80 %. Se centralizó esta condición en `app/api/topes.py`; las pruebas cubren 75 %, 80 % y 81 %. El formato del mensaje para otros porcentajes continúa sin especificar.
- Validación final: backend **35 passed** con cobertura de líneas/ramas; frontend **18 passed**; Ruff sin observaciones en los archivos Python modificados.
- Cobertura global backend: **85 %**. `Missing` concentra huecos en `api/gastos.py` (incluido resumen mensual y ramas de filtros), `services/receipt_reader.py` y `api/auth.py`. No se añadieron resultados para esas rutas sin criterios/escenarios suficientes.
- Las mutaciones conceptuales de 80 % exacto y menor al 80 % quedan protegidas por regresiones; no se modificó temporalmente el código para ejecutar mutación en esta sesión.

## 3. Sensibilidad de las pruebas ante fallos intencionales

Realicé una mutación a la vez sobre el código fuente. En cada caso, verifiqué que el archivo estuviera limpio antes de mutarlo y lo restauré posteriormente mediante `git restore`, sin modificar los valores esperados de las pruebas.

| Mutación temporal | Pruebas ejecutadas | Resultado de la mutación | Restauración |
| --- | --- | --- | --- |
| En `validar_fecha_gasto`, cambié la comparación de fecha futura para rechazar fechas pasadas. | `python -m pytest -v tests/test_validaciones.py::test_hu02_reglas_de_fecha_de_las_historias` | Detectada: fallaron los dos escenarios parametrizados; rechazó la fecha pasada y no rechazó la futura. | `git restore -- backend/app/domain/validaciones.py` |
| En `TopeCreate.validar_monto_tope`, permití cero cambiando la condición `<= 0` por `< 0`. | `python -m pytest -v tests/test_semana7.py -k hu07` | Detectada: falló el caso cero; al saltarse la validación, la base de datos lanzó `IntegrityError` en vez de responder el 422 esperado. Los casos positivo y negativo pasaron. | `git restore -- backend/app/schemas/tope.py` |
| En `listar_topes`, desactivé temporalmente `alerta_80`. | `python -m pytest -v tests/test_semana7.py -k hu08` | Detectada: falló el escenario del 81 %; el escenario sin tope pasó. | `git restore -- backend/app/api/topes.py` |

Las tres mutaciones fueron detectadas y restauradas. Al ejecutar nuevamente la suite completa después de restaurar los archivos, aprobaron las **33 pruebas** y **Ruff** pasó sin observaciones.

## 4. Datos sintéticos y fixture

Configuré las pruebas para utilizar el fixture local `contexto_sintetico` dentro de `backend/tests/test_semana7.py`. Este crea por API un usuario ficticio con correo único bajo `@prueba.local`, inicia sesión y obtiene las categorías locales sembradas por la aplicación. La configuración en `backend/tests/conftest.py` utiliza una base SQLite temporal, garantizando que no se toquen las bases locales del proyecto ni datos de personas reales.

El diccionario `datos` del fixture contiene:

- `comercio`: `Mercado Ñandú d'Oliva`, con tilde, `ñ` y apóstrofe, utilizado en los gastos sintéticos para confirmar que se acepta texto con caracteres especiales.
- `comercio_vacio`: cadena vacía incluida como dato difícil. No la utilicé para afirmar un resultado porque las historias no especifican ese caso.
- `monto_cero`: `0` y `monto_no_numerico`: `abc`, correspondientes a las entradas inválidas de HU-03.
- `monto_valido`: `85000`, valor de corrección especificado en HU-03.

Todos los valores de topes, fechas, categorías y gastos usados en las pruebas son ficticios. El caso de $320.000 se deriva del 80 % del tope explícito de $400.000; $300.000 ya aparece en el escenario existente de HU-08. No se utilizan datos de producción.