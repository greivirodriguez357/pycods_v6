import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from database import engine, Base, SessionLocal
from routers import auth, users, exercises, gamification, lessons, code
import models

Base.metadata.create_all(bind=engine)

def _migrate():
    """Agrega columnas nuevas a tablas que ya existían (sin perder datos)."""
    try:
        with engine.begin() as conn:
            if engine.dialect.name == "postgresql":
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS ultima_actividad DATE"))
    except Exception as e:
        print("[migración]", e)

def _seed_admin():
    """Crea el primer administrador desde las variables ADMIN_EMAIL y ADMIN_PASSWORD (si no existe)."""
    email, pwd = os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD")
    if not email or not pwd:
        return
    db = SessionLocal()
    try:
        if not db.query(models.User).filter(models.User.email == email).first():
            db.add(models.User(nombre="Administrador", email=email, hashed_password=auth.pwd_context.hash(pwd), rol=models.RoleEnum.admin))
            db.commit()
            print(f"[inicio] Administrador creado: {email}")
    finally:
        db.close()

_migrate()
_seed_admin()

app = FastAPI(
    title="Pycods API",
    description="API robusta para la plataforma educativa inclusiva Pycods (TEA)",
    version="2.0.0"
)

# Orígenes permitidos (frontend en 4042; 4200 por si usas `ng serve`)
origins = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:4042,http://127.0.0.1:4042,http://localhost:4200",
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(users.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(exercises.router, prefix="/api/exercises", tags=["Ejercicios y Progreso"])
app.include_router(code.router, prefix="/api/code", tags=["Ejecutar código"])
app.include_router(lessons.router, prefix="/api/lessons", tags=["Lecciones interactivas"])
app.include_router(gamification.router, prefix="/api/gamification", tags=["Gamificación y Monstruo"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")  # fotos de perfil

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Pycods - Inclusión + Tecnología + Diversión"}


@app.get("/health")
def health():
    return {"status": "ok"}
