from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_usuario, get_db
from app.crud import crud_servicio, crud_solicitud
from app.models.usuario import Usuario
from app.schemas.solicitud import Solicitud, SolicitudCrear

router = APIRouter(tags=["solicitudes"])


def _a_solicitud(s) -> Solicitud:
    return Solicitud(
        id=s.id,
        id_servicio=s.id_servicio,
        titulo_servicio=s.servicio.titulo if s.servicio else "",
        nombre_cliente=f"{s.cliente.nombre} {s.cliente.apellido}".strip() if s.cliente else "",
        correo_cliente=s.cliente.correo if s.cliente else "",
        celular_cliente=s.cliente.celular if s.cliente else "",
        mensaje=s.mensaje,
        atendida=s.atendida,
        creado_en=s.creado_en,
    )


@router.post(
    "/servicios/{id_servicio}/solicitar",
    response_model=Solicitud,
    status_code=status.HTTP_201_CREATED,
)
def solicitar_servicio(
    id_servicio: int,
    data: SolicitudCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    """Cualquier usuario logueado (Cliente o Trabajador actuando como
    cliente) puede solicitar un servicio aprobado. El trabajador dueño ve
    los datos de contacto de quien lo solicita en su panel."""
    servicio = crud_servicio.obtener(db, id_servicio)
    if servicio is None or servicio.estado != "aprobado":
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    if servicio.id_usuario == usuario.id:
        raise HTTPException(status_code=400, detail="No puedes solicitar tu propio servicio")

    solicitud = crud_solicitud.crear(db, data, id_cliente=usuario.id, id_servicio=id_servicio)
    return _a_solicitud(crud_solicitud.obtener(db, solicitud.id))


@router.get("/solicitudes/mias", response_model=list[Solicitud])
def mis_solicitudes_recibidas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    """Solicitudes que le han llegado a los servicios del usuario logueado."""
    return [_a_solicitud(s) for s in crud_solicitud.listar_recibidas_por_trabajador(db, usuario.id)]


@router.patch("/solicitudes/{id_solicitud}/atender", response_model=Solicitud)
def atender_solicitud(
    id_solicitud: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_usuario),
):
    solicitud = crud_solicitud.obtener(db, id_solicitud)
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.servicio.id_usuario != usuario.id:
        raise HTTPException(status_code=403, detail="Esta solicitud no es tuya")
    return _a_solicitud(crud_solicitud.marcar_atendida(db, solicitud))
