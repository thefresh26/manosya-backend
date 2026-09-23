"""Script de un solo uso: crea (o resetea) una cuenta de ADMINISTRADOR DE
PRUEBA, separada de cualquier admin real, para que Claude pueda probar el
panel de administrador sin que nadie tenga que compartir la contraseña real.

No interactivo a propósito (para correrlo de una sola vez sin prompts):

    cd backend
    venv\\Scripts\\activate
    python -m app.scripts.crear_admin_prueba

Correo y contraseña quedan fijos aquí abajo (son de prueba, no reales).
Puedes borrar esta cuenta después desde /admin o volviendo a correr este
mismo script no cambia nada grave: solo crea/reinicia esa cuenta de prueba.
"""

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import calificacion, categoria, modulo, modulo_por_rol, servicio  # noqa: F401
from app.models.rol import Rol
from app.models.usuario import Usuario

CORREO = "prueba.claude.admin@example.com"
CONTRASENA = "PruebaAdminSegura2026!"


def main():
    db = SessionLocal()
    try:
        rol_admin = db.query(Rol).filter(Rol.nombre == "Administrador").first()
        if rol_admin is None:
            rol_admin = Rol(nombre="Administrador", descripcion="Control total de la plataforma")
            db.add(rol_admin)
            db.commit()
            db.refresh(rol_admin)

        usuario = db.query(Usuario).filter(Usuario.correo == CORREO).first()
        if usuario:
            usuario.id_rol = rol_admin.id
            usuario.activo = True
            usuario.contrasena = hash_password(CONTRASENA)
            db.commit()
            print(f"Listo: {CORREO} actualizado a Administrador de prueba.")
        else:
            usuario = Usuario(
                correo=CORREO,
                contrasena=hash_password(CONTRASENA),
                nombre="Admin",
                apellido="DePrueba",
                cedula="000000999",
                celular="3000000999",
                ciudad="Barranquilla",
                direccion="N/A",
                activo=True,
                id_rol=rol_admin.id,
            )
            db.add(usuario)
            db.commit()
            print(f"Cuenta de administrador de prueba creada: {CORREO}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
