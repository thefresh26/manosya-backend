from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.security import hash_password
from app.models.calificacion import Calificacion
from app.models.rol import Rol
from app.models.servicio import Servicio
from app.models.usuario import Usuario
from app.schemas.usuario import RegistroTrabajador


def get_by_correo(db: Session, correo: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.correo == correo).first()


def get_by_cedula(db: Session, cedula: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.cedula == cedula).first()


def obtener_o_crear_rol_trabajador(db: Session) -> Rol:
    rol = db.query(Rol).filter(Rol.nombre == "Trabajador").first()
    if rol is None:
        rol = Rol(nombre="Trabajador", descripcion="Trabajador informal que ofrece servicios")
        db.add(rol)
        db.commit()
        db.refresh(rol)
    return rol


def registrar_trabajador(db: Session, data: RegistroTrabajador, foto_url: str | None = None) -> Usuario:
    rol = obtener_o_crear_rol_trabajador(db)
    usuario = Usuario(
        correo=data.correo,
        contrasena=hash_password(data.contrasena),
        nombre=data.nombre,
        apellido=data.apellido,
        cedula=data.cedula,
        celular=data.celular,
        ciudad=data.ciudad,
        direccion=data.direccion,
        latitud=data.latitud,
        longitud=data.longitud,
        foto_url=foto_url,
        id_rol=rol.id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def listar_trabajadores_con_ubicacion(db: Session) -> list[Usuario]:
    """Trabajadores activos con coordenadas válidas, para pintar en el mapa público."""
    rol = db.query(Rol).filter(Rol.nombre == "Trabajador").first()
    if rol is None:
        return []
    return (
        db.query(Usuario)
        .filter(
            Usuario.id_rol == rol.id,
            Usuario.activo.is_(True),
            Usuario.latitud.isnot(None),
            Usuario.longitud.isnot(None),
        )
        .all()
    )


def listar_destacados(db: Session, limite: int = 8) -> list[dict]:
    """Trabajadores activos con al menos un servicio activo publicado, con su
    oficio (categoría del servicio más reciente) y su calificación promedio
    real. Se usa en la sección "Trabajadores destacados" de la landing page,
    en vez de los datos de ejemplo de contenido.js."""
    trabajadores = (
        db.query(Usuario)
        .join(Servicio, Servicio.id_usuario == Usuario.id)
        .filter(Usuario.activo.is_(True), Servicio.activo.is_(True))
        .options(joinedload(Usuario.servicios).joinedload(Servicio.categoria))
        .distinct()
        .order_by(Usuario.id.desc())
        .limit(limite)
        .all()
    )

    resultado = []
    for usuario in trabajadores:
        activos = [s for s in usuario.servicios if s.activo]
        if not activos:
            continue
        principal = max(activos, key=lambda s: s.creado_en)

        promedio, total = (
            db.query(func.avg(Calificacion.puntuacion), func.count(Calificacion.id))
            .join(Servicio, Servicio.id == Calificacion.id_servicio)
            .filter(Servicio.id_usuario == usuario.id, Servicio.activo.is_(True))
            .first()
        )

        resultado.append(
            {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "ciudad": usuario.ciudad,
                "foto_url": usuario.foto_url,
                "oficio": principal.categoria.nombre if principal.categoria else principal.titulo,
                "bio": principal.descripcion,
                "total_calificaciones": total or 0,
                "calificacion_promedio": round(float(promedio), 1) if promedio is not None else None,
            }
        )
    return resultado


def listar_todos(db: Session) -> list[Usuario]:
    """Todos los usuarios registrados (cualquier rol), para el panel de administrador."""
    return db.query(Usuario).order_by(Usuario.id.desc()).all()


def obtener(db: Session, id_usuario: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id == id_usuario).first()


def desactivar(db: Session, usuario: Usuario) -> Usuario:
    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario


def reactivar(db: Session, usuario: Usuario) -> Usuario:
    usuario.activo = True
    db.commit()
    db.refresh(usuario)
    return usuario
