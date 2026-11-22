# Preguntas pendientes antes de producción

1. ¿Cuál será la URL HTTPS pública de la API para configurar
   `src/environments/environment.prod.ts`?
2. ¿La persistencia de producción debe seguir en SQLite o se desplegará
   PostgreSQL? Si será PostgreSQL, ¿qué servicio administrado y estrategia de
   migraciones se usarán?
3. ¿Se autoriza enviar fotos de recibos a Gemini u OpenAI, y cuál será el
   proveedor habilitado para cada entorno?
4. ¿Qué diez recibos reales se usarán para medir el objetivo de precisión
   (al menos 8/10) y el tiempo de respuesta de cinco segundos?
5. ¿Se publicará como app nativa Android/iOS además de web? Si es así, hay que
   confirmar la captura con cámara en cada plataforma y decidir si se requiere
   almacenamiento nativo seguro para fotos y tokens.
