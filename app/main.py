from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import calificacion, modulo, modulo_por_rol, rol, servicio, usuario  # noqa: F401
from app.models.categoria import Categoria

app = FastAPI(title="Plataforma de Servicios - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fotos de perfil subidas en el registro (ver app/core/uploads.py).
DIRECTORIO_STATIC = Path(__file__).resolve().parent / "static"
DIRECTORIO_STATIC.mkdir(parents=True, exist_ok=True)
(DIRECTORIO_STATIC / "fotos").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=DIRECTORIO_STATIC), name="static")

# Frontend ya compilado (SvelteKit + adapter-static), copiado aquí como
# archivos estáticos listos. Así el backend sirve tanto la API como las
# páginas del sitio, en un solo servidor y un solo servicio en Render.
# Si esta carpeta no existe (por ejemplo, en desarrollo local si aún no se
# ha compilado el frontend), el backend sigue funcionando solo como API.
DIRECTORIO_FRONTEND = Path(__file__).resolve().parent / "frontend_dist"
FRONTEND_DISPONIBLE = (DIRECTORIO_FRONTEND / "index.html").is_file()

if FRONTEND_DISPONIBLE:
    # Los archivos compilados (JS/CSS con nombres únicos) que SvelteKit
    # referencia con rutas absolutas como "/_app/immutable/...".
    app.mount(
        "/_app",
        StaticFiles(directory=DIRECTORIO_FRONTEND / "_app"),
        name="frontend_assets",
    )


CATEGORIAS_INICIALES = [
    {"nombre": "Plomería", "icono": "plomeria", "descripcion": "Reparación de fugas, instalaciones y destape de tuberías"},
    {"nombre": "Electricidad", "icono": "electricidad", "descripcion": "Instalaciones y reparaciones eléctricas residenciales"},
    {"nombre": "Aseo y limpieza", "icono": "limpieza", "descripcion": "Limpieza de hogares, apartamentos y oficinas"},
    {"nombre": "Jardinería", "icono": "jardineria", "descripcion": "Mantenimiento de jardines y zonas verdes"},
    {"nombre": "Pintura", "icono": "pintura", "descripcion": "Pintura de interiores y exteriores"},
    {"nombre": "Mudanzas", "icono": "mudanzas", "descripcion": "Transporte y mudanzas de hogares y oficinas"},
]


@app.on_event("startup")
def crear_tablas():
    Base.metadata.create_all(bind=engine)
    # Migración manual y minima (sin Alembic): agrega la columna `activo`
    # a usuario si la tabla ya existia de antes de que existiera este campo.
    # Necesaria para el panel de admin (desactivar cuentas en vez de borrarlas).
    with engine.begin() as conexion:
        conexion.execute(
            text("ALTER TABLE usuario ADD COLUMN IF NOT EXISTS activo BOOLEAN NOT NULL DEFAULT TRUE")
        )
        # Estado de aprobación del formulario de trabajo. Los formularios que
        # ya existían antes de este cambio quedan "aprobado" (mantienen el
        # comportamiento que ya tenían: visibles al público); los formularios
        # nuevos siempre entran como "pendiente" (ver crud_servicio.crear).
        conexion.execute(
            text(
                "ALTER TABLE servicio ADD COLUMN IF NOT EXISTS estado VARCHAR NOT NULL DEFAULT 'aprobado'"
            )
        )
        conexion.execute(
            text("ALTER TABLE servicio ADD COLUMN IF NOT EXISTS motivo_rechazo VARCHAR")
        )

    # Siembra las categorías base la primera vez que arranca el backend,
    # para que el frontend no dependa de datos de ejemplo (contenido.js).
    # No se repite si ya existen (evita duplicados en cada reinicio).
    db = SessionLocal()
    try:
        if db.query(Categoria).count() == 0:
            for datos in CATEGORIAS_INICIALES:
                db.add(Categoria(**datos))
            db.commit()
    finally:
        db.close()


app.include_router(api_router, prefix="/api/v1")


if FRONTEND_DISPONIBLE:
    @app.get("/{ruta_completa:path}", include_in_schema=False)
    def servir_frontend(ruta_completa: str):
        """
        Sirve el frontend ya compilado (SPA). Si la ruta pedida coincide con
        un archivo real dentro de frontend_dist (por ejemplo "robots.txt" o
        "favicon.png"), lo devuelve tal cual. Para cualquier otra ruta (por
        ejemplo "/registro", o rutas futuras del panel de admin) devuelve
        siempre "index.html": el enrutador de SvelteKit, ya cargado en el
        navegador, decide qué mostrar. Esta función se registra al final,
        después de "/api/v1/..." y "/static/...", para no interferir con
        esas rutas.
        """
        base = DIRECTORIO_FRONTEND.resolve()
        archivo_pedido = (base / ruta_completa).resolve()

        # Evita que alguien pida algo como "../../.env" y se salga de la
        # carpeta del frontend compilado.
        if base not in archivo_pedido.parents and archivo_pedido != base:
            archivo_pedido = base / "index.html"

        if archivo_pedido.is_file():
            return FileResponse(archivo_pedido)
        return FileResponse(base / "index.html")
else:
    @app.get("/")
    def root():
        return {"status": "ok", "mensaje": "API de la plataforma de servicios"}
