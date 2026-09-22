from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.api.deps import get_db, requerir_administrador
from app.crud import crud_servicio, crud_usuario
from app.models.servicio import Servicio
from app.models.usuario import Usuario
from app.schemas.estadisticas import EstadisticasAdmin
from app.schemas.servicio import RechazarServicio, ServicioConCategoria
from app.schemas.usuario import UsuarioAdmin

router = APIRouter(prefix="/admin", tags=["admin"])


def _a_servicio_con_categoria(servicio: Servicio) -> ServicioConCategoria:
    return ServicioConCategoria(
        id=servicio.id,
        id_usuario=servicio.id_usuario,
        id_categoria=servicio.id_categoria,
        titulo=servicio.titulo,
        descripcion=servicio.descripcion,
        precio_desde=servicio.precio_desde,
        disponibilidad=servicio.disponibilidad,
        foto_url=servicio.foto_url,
        activo=servicio.activo,
        estado=servicio.estado,
        motivo_rechazo=servicio.motivo_rechazo,
        creado_en=servicio.creado_en,
        categoria=servicio.categoria,
        nombre_trabajador=f"{servicio.usuario.nombre} {servicio.usuario.apellido}".strip()
        if servicio.usuario
        else None,
        ciudad_trabajador=servicio.usuario.ciudad if servicio.usuario else None,
    )


def _a_usuario_admin(usuario: Usuario) -> UsuarioAdmin:
    return UsuarioAdmin(
        id=usuario.id,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        cedula=usuario.cedula,
        celular=usuario.celular,
        ciudad=usuario.ciudad,
        direccion=usuario.direccion,
        activo=usuario.activo,
        id_rol=usuario.id_rol,
        nombre_rol=usuario.rol.nombre if usuario.rol else "",
    )


@router.get("/usuarios", response_model=list[UsuarioAdmin])
def listar_usuarios(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requerir_administrador),
):
    """Lista completa de personas registradas (cualquier rol). Solo accesible
    con una sesión de un usuario con rol Administrador."""
    return [_a_usuario_admin(u) for u in crud_usuario.listar_todos(db)]


@router.patch("/usuarios/{id_usuario}/desactivar", response_model=UsuarioAdmin)
def desactivar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(requerir_administrador),
):
    """"Desecha" a una persona: desactiva su cuenta (no la borra), para que
    deje de aparecer en el mapa público y no pueda iniciar sesión."""
    if id_usuario == admin.id:
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta de administrador")
    usuario = crud_usuario.obtener(db, id_usuario)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return _a_usuario_admin(crud_usuario.desactivar(db, usuario))


@router.patch("/usuarios/{id_usuario}/reactivar", response_model=UsuarioAdmin)
def reactivar_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requerir_administrador),
):
    """Revierte una desactivación, por si fue un error."""
    usuario = crud_usuario.obtener(db, id_usuario)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return _a_usuario_admin(crud_usuario.reactivar(db, usuario))


@router.get("/estadisticas", response_model=EstadisticasAdmin)
def obtener_estadisticas(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requerir_administrador),
):
    """Conteos para las tarjetas del panel de admin. Cuenta cuentas por rol
    (una persona nunca se cuenta dos veces, porque Cliente -> Trabajador es
    un ascenso de la misma cuenta) y formularios por estado."""
    por_rol = crud_usuario.contar_por_rol(db)
    por_estado_servicio = crud_servicio.contar_por_estado(db)
    return EstadisticasAdmin(
        total_clientes=por_rol.get("Cliente", 0),
        total_trabajadores=por_rol.get("Trabajador", 0),
        total_administradores=por_rol.get("Administrador", 0),
        formularios_pendientes=por_estado_servicio["pendiente"],
        formularios_aprobados=por_estado_servicio["aprobado"],
        formularios_rechazados=por_estado_servicio["rechazado"],
    )


@router.get("/servicios/pendientes", response_model=list[ServicioConCategoria])
def listar_servicios_pendientes(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requerir_administrador),
):
    """Formularios de trabajo esperando aprobación."""
    return [_a_servicio_con_categoria(s) for s in crud_servicio.listar_pendientes(db)]


@router.patch("/servicios/{id_servicio}/aprobar", response_model=ServicioConCategoria)
def aprobar_servicio(
    id_servicio: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requerir_administrador),
):
    """Aprueba un formulario: queda visible al público y, si el dueño todavía
    era Cliente, su cuenta asciende a Trabajador (misma cuenta, sin perder
    sus funciones de cliente)."""
    servicio = crud_servicio.obtener(db, id_servicio)
    if servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    servicio = crud_servicio.aprobar(db, servicio)

    dueno = servicio.usuario
    if dueno is not None and dueno.rol is not None and dueno.rol.nombre == "Cliente":
        rol_trabajador = crud_usuario.obtener_o_crear_rol_trabajador(db)
        dueno.id_rol = rol_trabajador.id
        db.commit()
        db.refresh(servicio)

    return _a_servicio_con_categoria(servicio)


@router.patch("/servicios/{id_servicio}/rechazar", response_model=ServicioConCategoria)
def rechazar_servicio(
    id_servicio: int,
    data: RechazarServicio,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requerir_administrador),
):
    """Rechaza un formulario. La cuenta del dueño no cambia de rol: sigue
    siendo Cliente (o Trabajador si ya tenía otro formulario aprobado antes)."""
    servicio = crud_servicio.obtener(db, id_servicio)
    if servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return _a_servicio_con_categoria(crud_servicio.rechazar(db, servicio, data.motivo))
