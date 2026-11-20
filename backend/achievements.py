"""Verificación automática de logros (equivalente a verificarLogros() del prototipo)."""
from sqlalchemy.orm import Session
import models

# (nombre, descripción, icono, XP, condición sobre las estadísticas del usuario)
ACHIEVEMENTS = [
    ("Primer paso", "Completaste tu primer reto", "🌱", 10, lambda s: s["retos"] >= 1),
    ("Explorador", "Completaste 3 retos", "🧭", 20, lambda s: s["retos"] >= 3),
    ("Memoria de elefante", "Ganaste una partida de parejas", "🐘", 10, lambda s: s["partidas"] >= 1),
    ("Coleccionista", "Compraste una parte para tu monstruo", "🎩", 10, lambda s: s["compras"] >= 1),
    ("Estrella brillante", "Llegaste al nivel 2", "🌟", 15, lambda s: s["nivel"] >= 2),
]

def _stats(db: Session, user: models.User):
    retos = (db.query(models.Progress.ejercicio_id)
               .filter(models.Progress.usuario_id == user.id, models.Progress.completado == True)  # noqa: E712
               .distinct().count())
    return {
        "retos": retos,
        "partidas": db.query(models.MemoryGame).filter(models.MemoryGame.usuario_id == user.id).count(),
        "compras": db.query(models.MonsterItem).filter(models.MonsterItem.usuario_id == user.id).count(),
        "nivel": user.nivel,
    }

def ensure_catalog(db: Session):
    existing = {a.nombre: a for a in db.query(models.Achievement).all()}
    created = False
    for nombre, desc, icono, xp, _ in ACHIEVEMENTS:
        if nombre not in existing:
            a = models.Achievement(nombre=nombre, descripcion=desc, icono=icono, recompensa_xp=xp)
            db.add(a); existing[nombre] = a; created = True
    if created:
        db.commit()
        existing = {a.nombre: a for a in db.query(models.Achievement).all()}
    return existing

def check_achievements(db: Session, user: models.User):
    """Desbloquea los logros que ya se cumplieron. Devuelve la lista de logros nuevos."""
    catalog = ensure_catalog(db)
    unlocked = {r.logro_id for r in db.query(models.UserAchievement).filter(models.UserAchievement.usuario_id == user.id)}
    stats = _stats(db, user)
    nuevos = []
    for nombre, desc, icono, xp, cond in ACHIEVEMENTS:
        ach = catalog[nombre]
        if ach.id not in unlocked and cond(stats):
            db.add(models.UserAchievement(usuario_id=user.id, logro_id=ach.id))
            user.xp += ach.recompensa_xp
            nuevos.append({"nombre": nombre, "descripcion": desc, "icono": icono, "xp": xp})
            stats["nivel"] = user.nivel
    if nuevos:
        while user.xp >= user.nivel * 100:
            user.nivel += 1
        db.commit()
    return nuevos
