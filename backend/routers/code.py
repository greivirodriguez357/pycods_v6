from fastapi import APIRouter, Depends
import models, schemas
from routers.auth import get_current_user
from safe_python import run_code

router = APIRouter()

@router.post("/run")
def run(data: schemas.CodeRun, _: models.User = Depends(get_current_user)):
    """Ejecuta el código del niño con el intérprete seguro (sin exec/eval ni acceso al sistema)."""
    return run_code(data.code)
