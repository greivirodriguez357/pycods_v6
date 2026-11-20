# Pycods - Plataforma Educativa Inclusiva (Full-Stack Integrada)

**Pycods** es una aplicación interactiva y gamificada orientada al aprendizaje del lenguaje de programación Python para niños con Trastorno del Espectro Autista (TEA).

## Arquitectura Integrada
- **Backend:** FastAPI, SQLAlchemy 2.0, PostgreSQL 15, Pydantic v2, JWT (bcrypt).
- **Frontend:** Angular 17, PrimeNG, AG Grid Community, PrimeFlex (Metodología TEACCH / Accesibilidad sensorial).
- **Orquestación:** Docker Compose (Base de datos PostgreSQL + API REST + Nginx Frontend).

## Instrucciones de Despliegue Automatizado (Docker)

1. Asegúrate de tener instalado **Docker** y **Docker Compose**.
2. En la raíz del proyecto, ejecuta:
   ```bash
   docker-compose up --build
   ```
3. Puertos de acceso:
   - **Frontend (Angular app):** `http://localhost:4042`
   - **Backend API REST:** `http://localhost:8001`
   - **Documentación Swagger / OpenAPI:** `http://localhost:8001/docs`

## Ejecución Local en Desarrollo (Sin Docker)

### Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # O venv\Scripts\activate en Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### Frontend:
```bash
cd frontend
npm install
npm start   # ng serve en http://localhost:4042 (proxy /api -> localhost:8001)
```

## App móvil (Expo Go)
La carpeta `mobile/` contiene la app para celular. Instrucciones en `mobile/README-MOBILE.md`.
El backend sirve a la web y al móvil: tras actualizar, reconstruye con `docker compose up --build -d`.

## Novedades de esta versión
- **Cuenta de administrador inicial:** `admin@pycods.com` / `Admin12345` (definida en `docker-compose.yml`; cámbiala).
  Los administradores ya no pueden crearse desde el registro; los crea otro administrador.
- **Recuperar contraseña:** en modo local el código aparece en pantalla y en `docker compose logs backend`
  (`SHOW_RESET_CODE: "true"`). Para producción pon `"false"` y configura `SMTP_HOST`, `SMTP_USER` y `SMTP_PASSWORD`.
- **Código seguro:** los retos de escribir código se ejecutan con un intérprete propio y limitado
  (`backend/safe_python.py`); no se usa `exec()` ni se puede acceder al sistema.
- **Fotos de perfil:** se guardan en el volumen `uploads_data`.
- **Racha:** se calcula con la hora de Colombia (`TZ_OFFSET_HOURS: "-5"`).
