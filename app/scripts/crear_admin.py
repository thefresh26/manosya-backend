"""Script para crear (o ascender) la cuenta de administrador.

A propósito NO es un endpoint HTTP: no queremos que nadie pueda crearse un
usuario Administrador desde el navegador ni con una petición. Este script se
corre una sola vez, directo en tu computador, con el entorno virtual
activado:

    cd backend
    venv\\Scripts\\activate
    python -m app.scripts.crear_admin

Te va a pedir los datos por consola. Si el correo ya existe, le cambia el rol
a Administrador y te pregunta si también quieres resetear la contraseña (útil
si ya te registraste como trabajador de prueba, o si la vez anterior tecleaste
mal la contraseña). Si no existe, crea una cuenta nueva. En ambos casos te
pide la contraseña dos veces, para detectar errores de tecleo (getpass no
muestra lo que escribes).
"""

import getpass

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import calificacion, categoria, modulo, modulo_por_rol, servicio  # noqa: F401
from app.models.rol import Rol
from app.models.usuario import Usuario


def obtener_o_crear_rol_administrador(db) -> Rol:
    rol = db.query(Rol).filter(Rol.nombre == "Administrador").first()
    if rol is None:
        rol = Rol(nombre="Administrador", descripcion="Control total de la plataforma")
        db.add(rol)
        db.commit()
        db.refresh(rol)
    return rol


def pedir_contrasena() -> str:
    """Pide la contraseña dos veces y repite hasta que coincidan, para
    detectar errores de tecleo (getpass no muestra lo que escribes)."""
    while True:
        contrasena = getpass.getpass("Contraseña: ")
        confirmacion = getpass.getpass("Repite la contraseña: ")
        if contrasena == confirmacion:
            return contrasena
        print("Las dos contraseñas no coinciden, intenta de nuevo.\n")


def main():
    db = SessionLocal()
    try:
        rol_admin = obtener_o_crear_rol_administrador(db)

        correo = input("Correo del administrador: ").strip()
        usuario = db.query(Usuario).filter(Usuario.correo == correo).first()

        if usuario:
            usuario.id_rol = rol_admin.id
            usuario.activo = True

            respuesta = input(
                "Ese correo ya existe. ¿También quieres resetear su contraseña? (s/n): "
            ).strip().lower()
            if respuesta == "s":
                usuario.contrasena = hash_password(pedir_contrasena())
                db.commit()
                print(f"Listo: {correo} ahora tiene rol Administrador y contraseña nueva.")
            else:
                db.commit()
                print(f"Listo: {correo} ahora tiene rol Administrador (contraseña sin cambios).")
            return

        print("Ese correo no existe todavía, se creará una cuenta nueva.")
        contrasena = pedir_contrasena()
        nombre = input("Nombre: ").strip()
        apellido = input("Apellido: ").strip()
        cedula = input("Cédula (puede ser cualquier número único, ej. 000000001): ").strip()
        celular = input("Celular (puede ser cualquiera, ej. 3000000000): ").strip()
        ciudad = input("Ciudad: ").strip()
        direccion = input("Dirección: ").strip()

        usuario = Usuario(
            correo=correo,
            contrasena=hash_password(contrasena),
            nombre=nombre,
            apellido=apellido,
            cedula=cedula,
            celular=celular,
            ciudad=ciudad,
            direccion=direccion,
            activo=True,
            id_rol=rol_admin.id,
        )
        db.add(usuario)
        db.commit()
        print(f"Cuenta de administrador creada: {correo}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
