from sqlalchemy.orm import Session, joinedload

from app.models.solicitud import Solicitud
from app.models.servicio import Servicio
from app.schemas.solicitud import SolicitudCrear


def crear(db: Session, data: SolicitudCrear, id_cliente: int, id_servicio: int) -> Solicitud:
    solicitud = Solicitud(id_cliente=id_cliente, id_servicio=id_servicio, mensaje=data.mensaje)
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud


def listar_recibidas_por_trabajador(db: Session, id_trabajador: int) -> list[Solicitud]:
    """Solicitudes de servicios que le pertenecen a este trabajador."""
    return (
        db.query(Solicitud)
        .join(Servicio, Solicitud.id_servicio == Servicio.id)
        .options(joinedload(Solicitud.cliente), joinedload(Solicitud.servicio))
        .filter(Servicio.id_usuario == id_trabajador)
        .order_by(Solicitud.creado_en.desc())
        .all()
    )


def obtener(db: Session, id_solicitud: int) -> Solicitud | None:
    return (
        db.query(Solicitud)
        .options(joinedload(Solicitud.cliente), joinedload(Solicitud.servicio))
        .filter(Solicitud.id == id_solicitud)
        .first()
    )


def marcar_atendida(db: Session, solicitud: Solicitud) -> Solicitud:
    solicitud.atendida = True
    db.commit()
    db.refresh(solicitud)
    return solicitud
