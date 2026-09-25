"""Script de un solo uso: llena la plataforma con datos de DEMOSTRACION
(trabajadores, clientes, servicios publicados, solicitudes y calificaciones)
para que el sitio no se vea vacio al mostrarlo o presentarlo.

Todas las cuentas usan el dominio de correo "@vozprofesional-demo.com" para
que sea facil identificarlas (y borrarlas mas adelante) sin confundirlas con
cuentas reales.

Es idempotente a nivel general: si ya existen las cuentas demo, no vuelve a
crear duplicados.

    cd backend
    venv\\Scripts\\activate
    python -m app.scripts.poblar_datos_prueba
"""

import random
from datetime import datetime, timedelta

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import (  # noqa: F401
    calificacion,
    denuncia_trabajador,
    modulo,
    modulo_por_rol,
    reporte_formulario,
)
from app.models.calificacion import Calificacion
from app.models.categoria import Categoria
from app.models.rol import Rol
from app.models.servicio import Servicio
from app.models.solicitud import Solicitud
from app.models.usuario import Usuario

DOMINIO_DEMO = "vozprofesional-demo.com"
CONTRASENA_DEMO = "DemoVozProfesional2026!"

CIUDADES = [
    ("Barranquilla", 10.9639, -74.7964),
    ("Soledad", 10.9185, -74.7813),
    ("Santa Marta", 11.2404, -74.1990),
    ("Cartagena", 10.3910, -75.4794),
    ("Sincelejo", 9.3047, -75.3978),
    ("Valledupar", 10.4631, -73.2532),
]

DISPONIBILIDADES = [
    "Disponible de inmediato",
    "Disponible esta semana",
    "Disponible fines de semana",
    "Disponible con cita previa",
]

# (nombre, apellido, categoria, titulo del servicio, descripcion, precio desde)
TRABAJADORES = [
    ("Carlos", "Martínez", "Plomería", "Plomería general y destape de tuberías", "Reparo fugas, cambio de llaves y destapo de tuberías con más de 8 años de experiencia.", 35000),
    ("Luis", "Ramírez", "Electricidad", "Instalación y reparación eléctrica residencial", "Instalaciones eléctricas certificadas, cambio de breakers y diagnóstico de cortocircuitos.", 40000),
    ("María", "González", "Aseo y limpieza", "Aseo profundo de hogares y apartamentos", "Limpieza general, desinfección de cocinas y baños, y organización de espacios.", 30000),
    ("Andrea", "López", "Jardinería", "Mantenimiento de jardines y zonas verdes", "Poda, siembra y mantenimiento general de jardines residenciales y conjuntos.", 25000),
    ("Jorge", "Pérez", "Pintura", "Pintura de interiores y exteriores", "Pintura de fachadas, interiores y acabados decorativos con acabado profesional.", 45000),
    ("Camila", "Torres", "Mudanzas", "Mudanzas y transporte de muebles", "Servicio de mudanza con vehículo propio, cuidado especial de muebles y electrodomésticos.", 80000),
    ("Ricardo", "Herrera", "Carpintería", "Fabricación y reparación de muebles en madera", "Muebles a la medida, reparación de puertas, closets y estructuras en madera.", 50000),
    ("Diana", "Cárdenas", "Cerrajería", "Apertura y cambio de cerraduras", "Apertura de puertas, cambio de cerraduras y duplicado de llaves las 24 horas.", 35000),
    ("Fernando", "Rojas", "Mecánica automotriz", "Mecánica automotriz a domicilio", "Diagnóstico, cambio de aceite y reparaciones menores de automóviles a domicilio.", 45000),
    ("Paola", "Salcedo", "Niñera y cuidado infantil", "Niñera con experiencia certificada", "Cuidado de niños en el hogar, apoyo en tareas y actividades recreativas.", 30000),
    ("Valentina", "Ospina", "Peluquería y belleza a domicilio", "Peluquería y belleza a domicilio", "Cortes, peinados, manicure y tratamientos de belleza en la comodidad de tu hogar.", 40000),
    ("Sebastián", "Mendoza", "Fotografía y video", "Fotografía y video para eventos", "Cobertura fotográfica y de video para eventos sociales, empresariales y familiares.", 150000),
    ("Katherine", "Vargas", "Reparación de electrodomésticos", "Reparación de lavadoras y neveras", "Diagnóstico y reparación de lavadoras, neveras y otros electrodomésticos.", 40000),
    ("Miguel", "Iguarán", "Domicilios y mensajería", "Mensajería y domicilios express", "Entrega de paquetes, encargos y domicilios rápidos dentro de la ciudad.", 12000),
    ("Laura", "Fontalvo", "Clases particulares y tutorías", "Tutorías de matemáticas y ciencias", "Clases de refuerzo escolar en matemáticas, física y química para todos los niveles.", 25000),
]

CLIENTES = [
    ("Alejandro", "Bermúdez"),
    ("Natalia", "Cuadrado"),
    ("Julián", "Escobar"),
    ("Daniela", "Peña"),
    ("Esteban", "Cantillo"),
    ("Mariana", "Del Río"),
    ("Óscar", "Barrios"),
    ("Sofía", "Meza"),
    ("Cristian", "Anaya"),
    ("Isabella", "Correa"),
]

MENSAJES_SOLICITUD = [
    "Hola, necesito el servicio para este fin de semana. ¿Tienen disponibilidad?",
    "Buenas, quisiera una cotización antes de confirmar la fecha.",
    "¿Podrían atenderme mañana en la tarde?",
    "Necesito el servicio con urgencia, quedo atento.",
    "Vi tu perfil y me gustaría contratar el servicio esta semana.",
]

COMENTARIOS_CALIFICACION = [
    "Excelente trabajo, muy puntual y profesional.",
    "Quedé muy satisfecho con el servicio, lo recomiendo.",
    "Buen trabajo, aunque llegó un poco tarde.",
    "Muy amable y cumplió con lo acordado.",
    "Rápido y de calidad, sin duda vuelvo a contratarlo.",
]


def obtener_o_crear_rol(db, nombre, descripcion):
    rol = db.query(Rol).filter(Rol.nombre == nombre).first()
    if rol is None:
        rol = Rol(nombre=nombre, descripcion=descripcion)
        db.add(rol)
        db.commit()
        db.refresh(rol)
    return rol


def main():
    db = SessionLocal()
    try:
        ya_existe = db.query(Usuario).filter(Usuario.correo.like(f"%@{DOMINIO_DEMO}")).count()
        if ya_existe > 0:
            print(f"Ya existen {ya_existe} cuentas demo. No se vuelve a poblar (script idempotente).")
            return

        rol_trabajador = obtener_o_crear_rol(db, "Trabajador", "Ofrece servicios en la plataforma")
        rol_cliente = obtener_o_crear_rol(db, "Cliente", "Solicita servicios en la plataforma")

        categorias_cache = {c.nombre: c for c in db.query(Categoria).all()}

        servicios_creados = []
        for i, (nombre, apellido, nombre_categoria, titulo, descripcion, precio) in enumerate(TRABAJADORES):
            ciudad, lat, lng = CIUDADES[i % len(CIUDADES)]
            correo = f"trabajador{i + 1}.demo@{DOMINIO_DEMO}"
            usuario = Usuario(
                correo=correo,
                contrasena=hash_password(CONTRASENA_DEMO),
                nombre=nombre,
                apellido=apellido,
                cedula=f"900{1000 + i}",
                celular=f"300{7000000 + i}",
                ciudad=ciudad,
                direccion=f"Calle {10 + i} # {20 + i}-{30 + i}",
                latitud=lat,
                longitud=lng,
                foto_url=None,
                id_rol=rol_trabajador.id,
                activo=True,
            )
            db.add(usuario)
            db.flush()

            categoria = categorias_cache.get(nombre_categoria)
            if categoria is None:
                print(f"Aviso: no se encontró la categoría '{nombre_categoria}', se omite ese servicio.")
                continue

            servicio = Servicio(
                id_usuario=usuario.id,
                id_categoria=categoria.id,
                titulo=titulo,
                descripcion=descripcion,
                precio_desde=precio,
                disponibilidad=random.choice(DISPONIBILIDADES),
                foto_url=None,
                activo=True,
                estado="aprobado",
                creado_en=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            )
            db.add(servicio)
            db.flush()
            servicios_creados.append(servicio)

        clientes_creados = []
        for i, (nombre, apellido) in enumerate(CLIENTES):
            ciudad, lat, lng = CIUDADES[i % len(CIUDADES)]
            correo = f"cliente{i + 1}.demo@{DOMINIO_DEMO}"
            usuario = Usuario(
                correo=correo,
                contrasena=hash_password(CONTRASENA_DEMO),
                nombre=nombre,
                apellido=apellido,
                cedula=f"800{1000 + i}",
                celular=f"301{7000000 + i}",
                ciudad=ciudad,
                direccion=f"Carrera {5 + i} # {15 + i}-{25 + i}",
                latitud=lat,
                longitud=lng,
                foto_url=None,
                id_rol=rol_cliente.id,
                activo=True,
            )
            db.add(usuario)
            db.flush()
            clientes_creados.append(usuario)

        db.commit()

        # Solicitudes: cada cliente le pide a 1 servicio al azar.
        for i, cliente in enumerate(clientes_creados):
            servicio = random.choice(servicios_creados)
            solicitud = Solicitud(
                id_cliente=cliente.id,
                id_servicio=servicio.id,
                mensaje=random.choice(MENSAJES_SOLICITUD),
                atendida=random.random() < 0.4,
                creado_en=datetime.utcnow() - timedelta(days=random.randint(0, 20)),
            )
            db.add(solicitud)

        # Calificaciones: 1 o 2 por cada servicio, con nombre de cliente libre.
        nombres_calificadores = [f"{n} {a}" for n, a in CLIENTES]
        for servicio in servicios_creados:
            for _ in range(random.randint(1, 2)):
                calif = Calificacion(
                    id_servicio=servicio.id,
                    nombre_cliente=random.choice(nombres_calificadores),
                    puntuacion=random.choice([4, 4, 5, 5, 5, 3]),
                    comentario=random.choice(COMENTARIOS_CALIFICACION),
                    creado_en=datetime.utcnow() - timedelta(days=random.randint(0, 45)),
                )
                db.add(calif)

        db.commit()
        print(
            f"Listo: {len(servicios_creados)} trabajadores con servicio publicado, "
            f"{len(clientes_creados)} clientes, solicitudes y calificaciones de prueba creadas."
        )
        print(f"Contraseña de todas las cuentas demo: {CONTRASENA_DEMO}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
