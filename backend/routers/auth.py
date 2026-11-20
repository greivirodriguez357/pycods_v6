from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
import secrets, smtplib
from email.message import EmailMessage
import streak
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey_pycods_tea")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    
    if user.rol == models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Las cuentas de administrador las crea otro administrador")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres")

    hashed_pwd = pwd_context.hash(user.password)
    new_user = models.User(
        nombre=user.nombre,
        email=user.email,
        hashed_password=hashed_pwd,
        rol=user.rol
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    
    access_token = create_access_token(data={"sub": user.email, "rol": user.rol.value})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """Devuelve el usuario dueño del token JWT (Authorization: Bearer ...)."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión no válida o expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if creds is None:
        raise unauthorized
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise unauthorized
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise unauthorized
    return user


def require_roles(*roles: str):
    def checker(user: models.User = Depends(get_current_user)):
        if user.rol.value not in roles:
            raise HTTPException(status_code=403, detail="No tienes permisos para esta acción")
        return user
    return checker


@router.get("/me", response_model=schemas.UserResponse)
def read_me(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    streak.refresh(db, current_user)
    return current_user


# ---------- Recuperación de contraseña ----------
def _send_email(to: str, code: str) -> bool:
    """Envía el código por correo si hay SMTP configurado (SMTP_HOST, SMTP_USER, SMTP_PASSWORD)."""
    host = os.getenv("SMTP_HOST")
    if not host:
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = "Tu código para recuperar tu cuenta de Pycods"
        msg["From"] = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", "pycods@localhost"))
        msg["To"] = to
        msg.set_content(f"Hola 👋\n\nTu código de recuperación es: {code}\nVence en 15 minutos.\n\nSi no fuiste tú, ignora este mensaje.")
        with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=10) as smtp:
            smtp.starttls()
            if os.getenv("SMTP_USER"):
                smtp.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD", ""))
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("[RECUPERACIÓN] No se pudo enviar el correo:", e)
        return False

@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotRequest, db: Session = Depends(get_db)):
    resp = {"message": "Si el correo está registrado, te enviamos un código de 6 dígitos. Vence en 15 minutos."}
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        return resp
    code = f"{secrets.randbelow(1000000):06d}"
    db.query(models.ResetCode).filter(models.ResetCode.usuario_id == user.id, models.ResetCode.usado == False).update({"usado": True})  # noqa: E712
    db.add(models.ResetCode(usuario_id=user.id, codigo_hash=pwd_context.hash(code), expira=datetime.utcnow() + timedelta(minutes=15)))
    db.commit()
    if not _send_email(user.email, code):
        # Modo local (sin servidor de correo): el código queda en los logs del backend
        print(f"[RECUPERACIÓN] Código para {user.email}: {code}  (docker compose logs backend)")
        if os.getenv("SHOW_RESET_CODE", "false").lower() == "true":
            resp["codigo_dev"] = code
    return resp

@router.post("/reset-password")
def reset_password(data: schemas.ResetRequest, db: Session = Depends(get_db)):
    invalid = HTTPException(status_code=400, detail="El código es incorrecto o ya venció")
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise invalid
    rc = (db.query(models.ResetCode)
            .filter(models.ResetCode.usuario_id == user.id, models.ResetCode.usado == False, models.ResetCode.expira > datetime.utcnow())  # noqa: E712
            .order_by(models.ResetCode.id.desc()).first())
    if not rc:
        raise invalid
    rc.intentos += 1
    if rc.intentos > 5:
        rc.usado = True
        db.commit()
        raise invalid
    if not pwd_context.verify(data.code.strip(), rc.codigo_hash):
        db.commit()
        raise invalid
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres")
    user.hashed_password = pwd_context.hash(data.new_password)
    rc.usado = True
    db.commit()
    return {"message": "¡Listo! Ya puedes entrar con tu nueva contraseña."}
