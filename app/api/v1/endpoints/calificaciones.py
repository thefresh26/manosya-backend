from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import crud_calificacion, crud_servicio
from app.schemas.calificacion import Calificacion, CalificacionCrear

router = APIRouter(prefix="/servicios/{id_servicio}/calificaciones", tags=["calificaciones"])


@router.get("", response_model=list[Calificacion])
def listar_calificaciones(id_servicio: int, db: Session = Depends(get_db)):
    return crud_calificacion.listar_por_servicio(db, id_servicio)


@router.post("", response_model=Calificacion, status_code=status.HTTP_201_CREATED)
def crear_calificacion(id_servicio: int, data: CalificacionCrear, db: Session = Depends(get_db)):
    # Prototipo académico: como todavía no hay registro de clientes, cualquier
    # persona puede calificar un servicio existente indicando su nombre.
    servicio = crud_servicio.obtener(db, id_servicio)
    if servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return crud_calificacion.crear(db, id_servicio, data)
