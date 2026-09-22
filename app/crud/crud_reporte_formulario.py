from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.reporte_formulario import ReporteFormulario
from app.schemas.reporte_formulario import ReporteFormularioCrear


def crear(db: Session, data: ReporteFormularioCrear, id_trabajador: int, id_servicio: int) -> ReporteFormulario:
    reporte = ReporteFormulario(
        id_trabajador=id_trabajador,
        id_servicio=id_servicio,
        descripcion=data.descripcion,
    )
    db.add(reporte)
    db.commit()
    db.refresh(reporte)
    return reporte


def listar_pendientes(db: Session) -> list[ReporteFormulario]:
    return (
        db.query(ReporteFormulario)
        .options(joinedload(ReporteFormulario.trabajador), joinedload(ReporteFormulario.servicio))
        .filter(ReporteFormulario.estado == "pendiente")
        .order_by(ReporteFormulario.creado_en.asc())
        .all()
    )


def obtener(db: Session, id_reporte: int) -> ReporteFormulario | None:
    return (
        db.query(ReporteFormulario)
        .options(joinedload(ReporteFormulario.trabajador), joinedload(ReporteFormulario.servicio))
        .filter(ReporteFormulario.id == id_reporte)
        .first()
    )


def resolver(db: Session, reporte: ReporteFormulario, resolucion: str) -> ReporteFormulario:
    reporte.estado = "resuelto"
    reporte.resolucion = resolucion
    reporte.resuelta_en = datetime.utcnow()
    db.commit()
    db.refresh(reporte)
    return reporte


def contar_pendientes(db: Session) -> int:
    return db.query(ReporteFormulario).filter(ReporteFormulario.estado == "pendiente").count()
