# Decisiones de implementación

## Persistencia offline

- Las fotos que esperan conexión se guardan como `Blob` en IndexedDB, no como
  Base64 en `localStorage`, para evitar el límite pequeño de almacenamiento de
  Web Storage.
- La cola conserva el orden de captura, recupera elementos que quedaron en
  estado `Procesando` tras cerrar la app y mantiene la foto si falla la lectura.
- Una lectura pendiente siempre se presenta en vista previa; solo se elimina de
  la cola después de guardar el gasto. Si se cancela, vuelve a quedar pendiente.
- Al abrir la cola se migran las fotos del formato Base64 anterior. La copia
  antigua solo se elimina después de confirmar que la escritura en IndexedDB
  terminó.

## Dashboard y temas

- El endpoint de gastos acepta un filtro diario o un par de fechas
  `fecha_inicio`/`fecha_fin`; la interfaz calcula los límites de semana y mes.
- El gráfico de pastel se dibuja con `conic-gradient` usando los totales de la
  API, sin añadir una dependencia de gráficos.
- El tema oscuro negro/azul es el inicial. La elección oscuro/claro se aplica
  sobre la paleta Ionic y se conserva en `localStorage`.
- Los controles mantienen tamaños compactos y esquinas redondeadas; el diseño
  usa variables para mantener contraste entre ambos temas.

## IA y pruebas

- `AI_PROVIDER` admite `mock`, `gemini` y `openai`; los proveedores reales usan
  claves disponibles únicamente en el entorno del backend.
- Las respuestas de IA se reducen a comercio, fecha y monto. JSON inválido se
  intenta leer dos veces dentro del límite de cuatro segundos; errores de red y
  tiempo de espera se traducen a HTTP 502 y 504.
- Las pruebas backend crean una base temporal por ejecución. No deben borrar ni
  reutilizar las bases locales del proyecto.

## Límites aún abiertos

- No se eligió el host de API de producción ni se configuró el terminador TLS.
- SQLite sigue siendo el valor local por defecto; no se añadieron migraciones de
  esquema ni se tomó una decisión de base de datos para producción.
- La captura usa el selector de archivos con `capture="environment"` para
  solicitar la cámara en navegadores móviles; aún se requiere validar el
  comportamiento en Android e iOS nativos.
