"""Script de un solo uso: agrega mas categorias de oficios informales a las
que ya existian (Plomeria, Electricidad, Aseo y limpieza, Jardineria,
Pintura, Mudanzas), para que el selector de categorias en "Publicar
formulario" (cuenta/+page.svelte) no se vea tan vacio.

Es idempotente: usa el nombre (que es unico en la tabla) para no duplicar
categorias que ya existan, sin importar cuantas veces se corra.

    cd backend
    venv\\Scripts\\activate
    python -m app.scripts.agregar_categorias
"""

from app.db.session import SessionLocal
from app.models import calificacion, modulo, modulo_por_rol, servicio, usuario, rol  # noqa: F401
from app.models.categoria import Categoria

NUEVAS_CATEGORIAS = [
    {"nombre": "Carpintería", "icono": "carpinteria", "descripcion": "Fabricación y reparación de muebles y estructuras en madera"},
    {"nombre": "Cerrajería", "icono": "cerrajeria", "descripcion": "Apertura, cambio e instalación de cerraduras y llaves"},
    {"nombre": "Albañilería", "icono": "albanileria", "descripcion": "Construcción, reparaciones y acabados en obra"},
    {"nombre": "Mecánica automotriz", "icono": "mecanica_auto", "descripcion": "Reparación y mantenimiento de automóviles"},
    {"nombre": "Mecánica de motos", "icono": "mecanica_motos", "descripcion": "Reparación y mantenimiento de motocicletas"},
    {"nombre": "Neveras y aires acondicionados", "icono": "refrigeracion", "descripcion": "Instalación y reparación de neveras y aires acondicionados"},
    {"nombre": "Instalación de gas", "icono": "gas", "descripcion": "Instalación y revisión de redes de gas domiciliario"},
    {"nombre": "Fumigación y control de plagas", "icono": "fumigacion", "descripcion": "Control de plagas en hogares y negocios"},
    {"nombre": "Niñera y cuidado infantil", "icono": "ninera", "descripcion": "Cuidado de niños en el hogar"},
    {"nombre": "Cuidado de adultos mayores", "icono": "cuidado_adultos", "descripcion": "Acompañamiento y cuidado de personas mayores"},
    {"nombre": "Cocina y catering", "icono": "cocina", "descripcion": "Preparación de alimentos para eventos y hogares"},
    {"nombre": "Costura y modistería", "icono": "costura", "descripcion": "Arreglos y confección de ropa"},
    {"nombre": "Peluquería y belleza a domicilio", "icono": "belleza", "descripcion": "Cortes, peinados y tratamientos de belleza a domicilio"},
    {"nombre": "Manicure y pedicure", "icono": "manicure", "descripcion": "Cuidado de uñas a domicilio"},
    {"nombre": "Masajes y spa a domicilio", "icono": "masajes", "descripcion": "Masajes y tratamientos de relajación a domicilio"},
    {"nombre": "Fotografía y video", "icono": "fotografia", "descripcion": "Cobertura fotográfica y de video para eventos"},
    {"nombre": "Diseño gráfico", "icono": "diseno_grafico", "descripcion": "Diseño de piezas gráficas y branding"},
    {"nombre": "Desarrollo web y software", "icono": "desarrollo_web", "descripcion": "Creación y mantenimiento de páginas web y aplicaciones"},
    {"nombre": "Clases particulares y tutorías", "icono": "tutorias", "descripcion": "Clases de refuerzo y tutorías personalizadas"},
    {"nombre": "Entrenador personal", "icono": "entrenador", "descripcion": "Rutinas de ejercicio y acompañamiento fitness"},
    {"nombre": "Paseador de mascotas", "icono": "paseador_mascotas", "descripcion": "Paseo y cuidado de mascotas"},
    {"nombre": "Peluquería canina", "icono": "peluqueria_canina", "descripcion": "Baño y corte de pelo para mascotas"},
    {"nombre": "Lavado de autos a domicilio", "icono": "lavado_autos", "descripcion": "Lavado y detallado de vehículos a domicilio"},
    {"nombre": "Instalación de pisos y cerámica", "icono": "pisos", "descripcion": "Instalación de pisos, baldosas y cerámica"},
    {"nombre": "Tapicería", "icono": "tapiceria", "descripcion": "Reparación y forrado de muebles"},
    {"nombre": "Vidriería y aluminio", "icono": "vidrieria", "descripcion": "Instalación de vidrios, ventanas y estructuras de aluminio"},
    {"nombre": "Techos e impermeabilización", "icono": "techos", "descripcion": "Reparación de techos y goteras"},
    {"nombre": "Soldadura y estructuras metálicas", "icono": "soldadura", "descripcion": "Trabajos en metal y estructuras soldadas"},
    {"nombre": "Instalación de cámaras de seguridad", "icono": "camaras_seguridad", "descripcion": "Instalación y configuración de cámaras de seguridad"},
    {"nombre": "Redes y cableado estructurado", "icono": "redes", "descripcion": "Instalación de redes de internet y cableado"},
    {"nombre": "Domicilios y mensajería", "icono": "mensajeria", "descripcion": "Entrega de paquetes y encargos"},
    {"nombre": "Transporte de carga", "icono": "transporte_carga", "descripcion": "Transporte de mercancía y mudanzas pequeñas"},
    {"nombre": "Eventos y decoración", "icono": "eventos", "descripcion": "Decoración y organización de eventos"},
    {"nombre": "Sonido e iluminación para eventos", "icono": "sonido", "descripcion": "Equipos de sonido e iluminación para fiestas y eventos"},
    {"nombre": "Reparación de electrodomésticos", "icono": "electrodomesticos", "descripcion": "Reparación de lavadoras, estufas y otros electrodomésticos"},
    {"nombre": "Reparación de celulares y computadores", "icono": "tecnologia", "descripcion": "Reparación de celulares, tablets y computadores"},
    {"nombre": "Traducción e idiomas", "icono": "traduccion", "descripcion": "Traducción de documentos y clases de idiomas"},
    {"nombre": "Trámites y contabilidad", "icono": "contabilidad", "descripcion": "Asesoría contable y gestión de trámites"},
    {"nombre": "Asesoría legal", "icono": "asesoria_legal", "descripcion": "Consultas y trámites legales"},
    {"nombre": "Arquitectura y diseño de interiores", "icono": "arquitectura", "descripcion": "Diseño y remodelación de espacios"},
]


def main():
    db = SessionLocal()
    agregadas = 0
    ya_existian = 0
    try:
        for datos in NUEVAS_CATEGORIAS:
            existe = db.query(Categoria).filter(Categoria.nombre == datos["nombre"]).first()
            if existe:
                ya_existian += 1
                continue
            db.add(Categoria(**datos))
            agregadas += 1
        db.commit()
    finally:
        db.close()
    print(f"Categorías agregadas: {agregadas} | ya existían: {ya_existian}")


if __name__ == "__main__":
    main()
