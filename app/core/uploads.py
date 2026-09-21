"""Guarda las fotos de perfil que suben los trabajadores al registrarse.

Prototipo académico: se guardan como archivos sueltos en app/static/fotos y se
sirven con StaticFiles (ver main.py). Para producción real esto iría a un
bucket (S3, Cloudinary, etc.), pero para el proyecto de clase esto es
suficiente y no agrega dependencias nuevas.
"""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

TIPOS_PERMITIDOS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024  # 5 MB

DIRECTORIO_ESTATICO = Path(__file__).resolve().parent.parent / "static" / "fotos"


def _extension_real(contenido: bytes) -> str | None:
    """Detecta el tipo de imagen mirando los primeros bytes del archivo (su
    "firma"), en vez de confiar en el Content-Type que manda el navegador,
    que cualquiera puede falsificar fácilmente. Devuelve None si no coincide
    con ninguno de los formatos permitidos."""
    if contenido[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if contenido[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if contenido[:4] == b"RIFF" and contenido[8:12] == b"WEBP":
        return ".webp"
    return None


async def guardar_foto_perfil(archivo: UploadFile | None) -> str | None:
    """Valida y guarda la foto de perfil subida en el registro.

    Devuelve la URL relativa (`/static/fotos/<archivo>`) para guardar en la
    base de datos, o None si no se envió ninguna foto.
    """
    if archivo is None or not archivo.filename:
        return None

    if archivo.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail="La foto debe ser JPG, PNG o WEBP.",
        )

    contenido = await archivo.read()
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(status_code=400, detail="La foto no puede pesar más de 5 MB.")

    extension = _extension_real(contenido)
    if extension is None:
        raise HTTPException(
            status_code=400,
            detail="El archivo no es una imagen JPG, PNG o WEBP válida.",
        )

    DIRECTORIO_ESTATICO.mkdir(parents=True, exist_ok=True)
    nombre_archivo = f"{uuid.uuid4().hex}{extension}"
    ruta = DIRECTORIO_ESTATICO / nombre_archivo
    ruta.write_bytes(contenido)

    return f"/static/fotos/{nombre_archivo}"
