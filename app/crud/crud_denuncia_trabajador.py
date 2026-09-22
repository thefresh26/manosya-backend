from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.denuncia_trabajador import DenunciaTrabajador
from app.schemas.denuncia_trabajador import DenunciaTrabajadorCrear


def crear(db: Session, data: DenunciaTrabajadorCrear, id_denunciante: int, id_trabajador: int) -> DenunciaTrabajador:
    denuncia = DenunciaTrabajador(
        id_denunciante=id_denunciante,
        id_trabajador=id_trabajador,
        id_servicio=data.id_servicio,
        motivo=data.motivo,
        descripcion=data.descripcion,
    )
    db.add(denuncia)
    db.commit()
    db.refresh(denuncia)
    return denuncia


def listar_pendientes(db: Session) -> list[DenunciaTrabajador]:
    return (
        db.query(DenunciaTrabajador)
        .options(joinedload(DenunciaTrabajador.denunciante), joinedload(DenunciaTrabajador.trabajador))
        .filter(DenunciaTrabajador.estado == "pendiente")
        .order_by(DenunciaTrabajador.creado_en.asc())
        .all()
    )


def obtener(db: Session, id_denuncia: int) -> DenunciaTrabajador | None:
    return (
        db.query(DenunciaTrabajador)
        .options(joinedload(DenunciaTrabajador.denunciante), joinedload(DenunciaTrabajador.trabajador))
        .filter(DenunciaTrabajador.id == id_denuncia)
        .first()
    )


def resolver(db: Session, denuncia: DenunciaTrabajador, resolucion: str) -> DenunciaTrabajador:
    denuncia.estado = "resuelta"
    denuncia.resolucion = resolucion
    denuncia.resuelta_en = datetime.utcnow()
    db.commit()
    db.refresh(denuncia)
    return denuncia


def contar_pendientes(db: Session) -> int:
    return db.query(DenunciaTrabajador).filter(DenunciaTrabajador.estado == "pendiente").count()
