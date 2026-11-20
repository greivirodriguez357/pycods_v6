"""Racha de días de práctica (usa la hora de Colombia, UTC-5, configurable)."""
import datetime
import os

OFFSET = int(os.getenv("TZ_OFFSET_HOURS", "-5"))

def today() -> datetime.date:
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=OFFSET)).date()

def touch(db, user):
    """Llamar cuando el niño practica (completa un reto o juego). Sube o reinicia la racha."""
    t, last = today(), user.ultima_actividad
    if last == t:
        return
    user.racha = (user.racha or 0) + 1 if last == t - datetime.timedelta(days=1) else 1
    user.ultima_actividad = t
    db.commit()

def refresh(db, user):
    """Si pasó más de un día sin practicar, la racha vuelve a 0 (sin castigo: se puede empezar de nuevo)."""
    last = user.ultima_actividad
    if user.racha and last and last < today() - datetime.timedelta(days=1):
        user.racha = 0
        db.commit()
