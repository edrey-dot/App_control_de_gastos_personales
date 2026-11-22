# Control de gastos personales

## 1. ¿Qué es?

Aplicación para registrar gastos personales, definir topes mensuales por
categoría y consultar resúmenes. El frontend está hecho con Ionic y Angular; el
backend ofrece una API FastAPI con autenticación JWT y base de datos SQLite por
defecto. La lectura de recibos funciona en modo simulado, Gemini u OpenAI.
Incluye filtros de gastos por día, semana, mes o rango, un resumen con gráfico
de pastel, una cola de recibos persistente sin conexión y cambio manual entre
tema oscuro negro/azul y claro blanco/azul.

Las cuentas nuevas incluyen nombre para mostrar, correo y celular colombiano
(10 dígitos, con prefijo `+57` opcional); se puede iniciar sesión con correo o
celular y contraseña. El celular no se verifica por SMS. El perfil permite
cambiar únicamente el nombre para mostrar y guardar una foto de hasta 2 MB en la
base de datos del backend, disponible en otros dispositivos mediante rutas
autenticadas. El correo y el celular no se editan desde el perfil.

## 2. Requisitos

- Windows 10/11 (los comandos de esta guía usan PowerShell).
- Python 3.10.
- Node.js 24.15 o posterior de la rama 24 y npm 8 o posterior (Angular CLI
  22.2.4 admite Node 22.22.3, 24.15 o versiones 26+).
- Git para clonar el repositorio.

## 3. Instalación

Clona el repositorio y abre PowerShell en su carpeta `App_gastos`. Continúa con:

```powershell
Set-Location .\backend
```

Configura el backend:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install ruff==0.17.5 pip-audit==2.10.1
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(32))"
notepad .env
```

Copia el valor generado en `SECRET_KEY` dentro de `.env`. No compartas ese
archivo ni subas claves al repositorio. Para uso local deja `AI_PROVIDER=mock`;
no se necesita una clave de Gemini.

Configura el frontend desde la raíz del proyecto:

```powershell
Set-Location ..
npm ci
```

## 4. Ejecución

Abre dos terminales de PowerShell.

En la primera, desde `App_gastos\backend`:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000` y su documentación
interactiva en `http://localhost:8000/docs`.

En la segunda, desde la raíz `App_gastos`:

```powershell
npm start
```

Abre `http://localhost:4200`. Para habilitar la lectura real de recibos, define
`AI_PROVIDER=gemini` y `GEMINI_API_KEY`, o `AI_PROVIDER=openai` y
`OPENAI_API_KEY`, en el `.env` del backend. Las claves se mantienen en el
servidor; nunca las configures en el frontend.

El frontend guarda la preferencia del tema y las fotos pendientes en el
almacenamiento local del navegador (IndexedDB). Al recuperar conexión, intenta
procesar las fotos en orden y muestra cada lectura para confirmación antes de
crear el gasto.

**Antes de desplegar:** `src/environments/environment.prod.ts` todavía apunta a
`http://localhost:8000`. Configura allí la URL HTTPS real de la API; el
certificado TLS y el servidor de producción no forman parte de este proyecto.

## 5. Pruebas y verificaciones

Desde `App_gastos\backend`, activa el entorno virtual y ejecuta:

```powershell
python -m pytest -q
ruff check .
pip-audit -r requirements.txt
```

Las pruebas backend usan una base SQLite temporal creada por
`backend/tests/conftest.py`; no eliminan ni modifican las bases de datos locales.

Para las pruebas unitarias del frontend, desde la raíz:

```powershell
npm run test:unit
```

Para las pruebas end-to-end con Playwright, instala Chromium una vez y ejecuta:

```powershell
npx playwright install chromium
npm run test:e2e
```

La suite frontend incluye pruebas de tema, filtros HTTP y almacenamiento de
recibos pendientes.

## 6. Estructura del proyecto

```text
App_gastos/
├── backend/
│   ├── app/api/          # Endpoints FastAPI
│   ├── app/core/         # Configuración y seguridad
│   ├── app/db/           # Modelos y sesión SQLAlchemy
│   ├── app/schemas/      # Esquemas Pydantic
│   ├── app/services/     # Lectura de recibos
│   └── tests/            # Pruebas del backend
├── src/app/              # Páginas, servicios y componentes Ionic/Angular
├── e2e/                  # Pruebas end-to-end del frontend
├── DECISIONES.md         # Decisiones de implementación y límites conocidos
├── PREGUNTAS.md          # Datos aún necesarios para producción/aceptación
├── README.md
└── bitacora_ia.md
```

## 7. Uso de inteligencia artificial

La aplicación ofrece un lector simulado para desarrollo y un lector Gemini
opcional. En modo Gemini, el backend envía la imagen del recibo a la API de
Google para extraer comercio, fecha y monto; no guarda la imagen en la base de
datos. Revisa y confirma los datos antes de registrar el gasto. No cargues
recibos con información que no quieras compartir con el proveedor externo.
Protege `GEMINI_API_KEY` como una contraseña y mantenla únicamente en el entorno
del backend.

## 8. Autor y licencia

- Autor: Yeison Edrey Rodriguez Hernandez
- Licencia: MIT © 2026 Yeison Edrey Rodriguez Hernandez. Uso libre con atribución al autor.
