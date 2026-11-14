# Control de gastos personales

## 1. ¿Qué es?

Aplicación para registrar gastos personales, definir topes mensuales por
categoría y consultar resúmenes. El frontend está hecho con Ionic y Angular; el
backend ofrece una API FastAPI con autenticación JWT y base de datos SQLite por
defecto. La lectura de recibos funciona en modo simulado o mediante Gemini.

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
`AI_PROVIDER=gemini` y `GEMINI_API_KEY` en el `.env` del backend. La clave se
mantiene en el servidor; nunca la configures en el frontend.

## 5. Pruebas y verificaciones

Desde `App_gastos\backend`, activa el entorno virtual y ejecuta:

```powershell
Remove-Item .\gastos.db -ErrorAction SilentlyContinue
python -m pytest -q
ruff check .
pip-audit -r requirements.txt
```

**Advertencia H-07:** las pruebas comparten `backend\gastos.db` y dejan datos
persistidos. Hasta aislar la base de datos de pruebas, elimina ese archivo antes
de cada ejecución de `pytest`. Esto borra los datos locales guardados en esa
base; respáldala primero si necesitas conservarlos. No se modificó ninguna
prueba existente para ocultar este problema.

Para las pruebas unitarias del frontend, desde la raíz:

```powershell
npm run test:unit
```

En la revisión del 2026-11-14 este comando compiló y reportó 2 pruebas
aprobadas, pero Vitest terminó con un error asíncrono `NG04002` al navegar a
`/login` desde `src/app/home/home.page.spec.ts`. Queda pendiente; no se modificó
esa prueba existente.

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
