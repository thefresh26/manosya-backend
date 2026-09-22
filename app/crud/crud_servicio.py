from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.servicio import Servicio
from app.models.usuario import Usuario
from app.schemas.servicio import ServicioCrear


def listar_activos(db: Session, id_categoria: int | None = None) -> list[Servicio]:
    """Servicios visibles públicamente: solo los que un administrador ya
    aprobó, del dueño desactivado ni el propio servicio desactivado."""
    consulta = (
        db.query(Servicio)
        .join(Usuario, Servicio.id_usuario == Usuario.id)
        .options(joinedload(Servicio.categoria), joinedload(Servicio.usuario))
        .filter(
            Servicio.activo.is_(True),
            Servicio.estado == "aprobado",
            Usuario.activo.is_(True),
        )
    )
    if id_categoria is not None:
        consulta = consulta.filter(Servicio.id_categoria == id_categoria)
    return consulta.order_by(Servicio.creado_en.desc()).all()


def obtener(db: Session, id_servicio: int) -> Servicio | None:
    return (
        db.query(Servicio)
        .options(joinedload(Servicio.categoria), joinedload(Servicio.usuario))
        .filter(Servicio.id == id_servicio)
        .first()
    )


def listar_por_usuario(db: Session, id_usuario: int) -> list[Servicio]:
    """Todos los formularios de un usuario, sin importar el estado (para que
    él mismo vea los suyos pendientes o rechazados, no solo los aprobados)."""
    return (
        db.query(Servicio)
        .options(joinedload(Servicio.categoria))
        .filter(Servicio.id_usuario == id_usuario)
        .order_by(Servicio.creado_en.desc())
        .all()
    )


def listar_pendientes(db: Session) -> list[Servicio]:
    """Formularios esperando revisión del administrador."""
    return (
        db.query(Servicio)
        .options(joinedload(Servicio.categoria), joinedload(Servicio.usuario))
        .filter(Servicio.estado == "pendiente")
        .order_by(Servicio.creado_en.asc())
        .all()
    )


def crear(db: Session, data: ServicioCrear, id_usuario: int, foto_url: str | None = None) -> Servicio:
    servicio = Servicio(
        id_usuario=id_usuario,
        id_categoria=data.id_categoria,
        titulo=data.titulo,
        descripcion=data.descripcion,
        precio_desde=data.precio_desde,
        disponibilidad=data.disponibilidad,
        foto_url=foto_url,
        estado="pendiente",
    )
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


def desactivar(db: Session, servicio: Servicio) -> Servicio:
    servicio.activo = False
    db.commit()
    db.refresh(servicio)
    return servicio


def aprobar(db: Session, servicio: Servicio) -> Servicio:
    servicio.estado = "aprobado"
    servicio.motivo_rechazo = None
    db.commit()
    db.refresh(servicio)
    return servicio


def rechazar(db: Session, servicio: Servicio, motivo: str | None) -> Servicio:
    servicio.estado = "rechazado"
    servicio.motivo_rechazo = motivo
    db.commit()
    db.refresh(servicio)
    return servicio


def contar_por_estado(db: Session) -> dict[str, int]:
    filas = (
        db.query(Servicio.estado, func.count(Servicio.id))
        .group_by(Servicio.estado)
        .all()
    )
    conteos = {"pendiente": 0, "aprobado": 0, "rechazado": 0}
    for estado, cantidad in filas:
        conteos[estado] = cantidad
    return conteos
