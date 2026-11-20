import base64, datetime, os, uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas, streak
from routers.auth import get_current_user, require_roles

router = APIRouter()
STAFF = ("admin", "docente")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
PRESET_AVATARS = {"avatar1", "avatar2", "avatar3", "avatar4"}

# IMPORTANTE: las rutas fijas ("/me", "/stats") van antes que "/{user_id}"

# ---------- Mi cuenta ----------
@router.patch("/me", response_model=schemas.UserResponse)
def update_me(data: schemas.UserUpdate, db: Session = Depends(get_db),
              current_user: models.User = Depends(get_current_user)):
    if data.avatar is not None:
        if data.avatar not in PRESET_AVATARS:
            raise HTTPException(status_code=400, detail="Avatar no válido")
        _delete_photo(current_user.avatar)
        current_user.avatar = data.avatar
    db.commit()
    db.refresh(current_user)
    return current_user

def _delete_photo(avatar):
    if avatar and avatar.startswith("foto:"):
        try:
            os.remove(os.path.join(UPLOAD_DIR, os.path.basename(avatar[5:])))
        except OSError:
            pass

@router.post("/me/avatar-photo", response_model=schemas.UserResponse)
def upload_avatar_photo(data: schemas.AvatarPhoto, db: Session = Depends(get_db),
                        current_user: models.User = Depends(get_current_user)):
    """Foto de perfil desde la cámara o la galería (JPG/PNG, máx. ~3 MB)."""
    try:
        img = base64.b64decode(data.image_base64.split(",")[-1])
    except Exception:
        raise HTTPException(status_code=400, detail="No pude leer la foto")
    if len(img) > 3_000_000:
        raise HTTPException(status_code=413, detail="La foto es muy pesada. Prueba con una más pequeña")
    if img[:3] == b"\xff\xd8\xff":
        ext = "jpg"
    elif img[:8] == b"\x89PNG\r\n\x1a\n":
        ext = "png"
    else:
        raise HTTPException(status_code=400, detail="Solo se aceptan fotos JPG o PNG")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    name = f"{current_user.id}_{uuid.uuid4().hex[:10]}.{ext}"
    with open(os.path.join(UPLOAD_DIR, name), "wb") as f:
        f.write(img)
    _delete_photo(current_user.avatar)
    current_user.avatar = f"foto:{name}"
    db.commit()
    db.refresh(current_user)
    return current_user

# ---------- Panel docente / admin ----------
@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _: models.User = Depends(require_roles(*STAFF))):
    users = db.query(models.User).all()
    t = streak.today()
    est = [u for u in users if u.rol.value == "estudiante"]
    retos = []
    for e in db.query(models.Exercise).order_by(models.Exercise.id):
        n = (db.query(models.Progress.usuario_id)
               .filter(models.Progress.ejercicio_id == e.id, models.Progress.completado == True)  # noqa: E712
               .distinct().count())
        retos.append({"titulo": e.titulo, "completados": n})
    return {
        "total": len(users),
        "estudiantes": len(est),
        "docentes": len([u for u in users if u.rol.value == "docente"]),
        "admins": len([u for u in users if u.rol.value == "admin"]),
        "activos_hoy": len([u for u in users if u.ultima_actividad == t]),
        "activos_semana": len([u for u in users if u.ultima_actividad and u.ultima_actividad >= t - datetime.timedelta(days=6)]),
        "promedio_xp": round(sum(u.xp for u in est) / len(est)) if est else 0,
        "partidas_memoria": db.query(models.MemoryGame).count(),
        "retos": retos,
    }

@router.get("/", response_model=List[schemas.UserResponse])
def get_users(skip: int = 0, limit: int = 200, db: Session = Depends(get_db),
              _: models.User = Depends(require_roles(*STAFF))):
    return db.query(models.User).order_by(models.User.id).offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_roles(*STAFF))):
    return _get_or_404(db, user_id)

@router.get("/{user_id}/detail")
def get_user_detail(user_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_roles(*STAFF))):
    """Avance de un estudiante: retos completados, logros y partidas."""
    u = _get_or_404(db, user_id)
    done_ids = {r[0] for r in db.query(models.Progress.ejercicio_id)
                .filter(models.Progress.usuario_id == u.id, models.Progress.completado == True).all()}  # noqa: E712
    retos = [{"titulo": e.titulo, "completado": e.id in done_ids} for e in db.query(models.Exercise).order_by(models.Exercise.id)]
    logros = [a.nombre for a in db.query(models.Achievement)
              .join(models.UserAchievement, models.UserAchievement.logro_id == models.Achievement.id)
              .filter(models.UserAchievement.usuario_id == u.id)]
    return {
        "id": u.id, "nombre": u.nombre, "email": u.email, "rol": u.rol.value, "nivel": u.nivel, "xp": u.xp,
        "monedas": u.monedas, "racha": u.racha, "ultima_actividad": str(u.ultima_actividad) if u.ultima_actividad else None,
        "retos": retos, "logros": logros,
        "partidas_memoria": db.query(models.MemoryGame).filter(models.MemoryGame.usuario_id == u.id).count(),
    }

@router.patch("/{user_id}", response_model=schemas.UserResponse)
def admin_update_user(user_id: int, data: schemas.UserAdminUpdate, db: Session = Depends(get_db),
                      actor: models.User = Depends(require_roles(*STAFF))):
    u = _get_or_404(db, user_id)
    _check_can_manage(actor, u)
    changes = data.dict(exclude_unset=True)
    if "rol" in changes and changes["rol"] is not None and actor.rol.value != "admin":
        raise HTTPException(status_code=403, detail="Solo un administrador puede cambiar roles")
    for field, value in changes.items():
        if value is None:
            continue
        if field in ("nivel", "xp", "monedas", "vidas") and value < 0:
            raise HTTPException(status_code=400, detail=f"{field} no puede ser negativo")
        if field == "nombre" and not value.strip():
            raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")
        setattr(u, field, value.strip() if field == "nombre" else value)
    db.commit()
    db.refresh(u)
    return u

@router.delete("/{user_id}")
def admin_delete_user(user_id: int, db: Session = Depends(get_db), actor: models.User = Depends(require_roles(*STAFF))):
    u = _get_or_404(db, user_id)
    if u.id == actor.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
    _check_can_manage(actor, u)
    for model, col in ((models.Progress, "usuario_id"), (models.UserAchievement, "usuario_id"), (models.MonsterItem, "usuario_id"),
                       (models.MemoryGame, "usuario_id"), (models.ResetCode, "usuario_id"), (models.Monster, "usuario_id")):
        db.query(model).filter(getattr(model, col) == u.id).delete()
    _delete_photo(u.avatar)
    db.delete(u)
    db.commit()
    return {"message": "Usuario eliminado"}

def _get_or_404(db, user_id):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u

def _check_can_manage(actor, target):
    """Un docente solo gestiona estudiantes; un admin gestiona a todos."""
    if actor.rol.value != "admin" and target.rol.value != "estudiante":
        raise HTTPException(status_code=403, detail="Un docente solo puede gestionar estudiantes")
