from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.calificacion import Calificacion
from app.schemas.calificacion import CalificacionCrear


def listar_por_servicio(db: Session, id_servicio: int) -> list[Calificacion]:
    return (
        db.query(Calificacion)
        .filter(Calificacion.id_servicio == id_servicio)
        .order_by(Calificacion.creado_en.desc())
        .all()
    )


def promedio_y_total(db: Session, id_servicio: int) -> tuple[float | None, int]:
    resultado = (
        db.query(func.avg(Calificacion.puntuacion), func.count(Calificacion.id))
        .filter(Calificacion.id_servicio == id_servicio)
        .first()
    )
    promedio, total = resultado
    return (round(float(promedio), 1) if promedio is not None else None, total or 0)


def crear(db: Session, id_servicio: int, data: CalificacionCrear) -> Calificacion:
    calificacion = Calificacion(id_servicio=id_servicio, **data.model_dump())
    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)
    return calificacion
