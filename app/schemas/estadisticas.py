from pydantic import BaseModel


class EstadisticasAdmin(BaseModel):
    """Conteos para las tarjetas del panel de administrador. Cada cuenta
    tiene un único rol a la vez, así que estos números nunca duplican a una
    misma persona (ver crud_usuario.contar_por_rol)."""

    total_clientes: int
    total_trabajadores: int
    total_administradores: int
    formularios_pendientes: int
    formularios_aprobados: int
    formularios_rechazados: int
    denuncias_trabajador_pendientes: int
    reportes_formulario_pendientes: int
