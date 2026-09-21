"""Límite simple de intentos de login, para frenar ataques de fuerza bruta
(probar contraseñas una tras otra hasta acertar).

Es intencionalmente simple (un diccionario en memoria, sin dependencias
nuevas como Redis): suficiente para un proyecto académico con un solo
proceso de backend. Si el servicio se reinicia (por ejemplo al "dormir" en
el plan gratuito de Render), el contador se resetea, lo cual es aceptable
para este caso de uso.
"""

import threading
import time

MAX_INTENTOS = 5
VENTANA_SEGUNDOS = 15 * 60  # 15 minutos

_lock = threading.Lock()
# correo -> (cantidad_de_fallos, momento_del_primer_fallo)
_intentos: dict[str, tuple[int, float]] = {}


def segundos_de_bloqueo_restantes(correo: str) -> int:
    """Devuelve cuántos segundos le faltan a este correo para poder volver a
    intentar login, o 0 si todavía tiene intentos disponibles."""
    with _lock:
        registro = _intentos.get(correo.lower())
        if registro is None:
            return 0
        cantidad, primer_fallo = registro
        transcurrido = time.time() - primer_fallo
        if transcurrido >= VENTANA_SEGUNDOS:
            del _intentos[correo.lower()]
            return 0
        if cantidad < MAX_INTENTOS:
            return 0
        return int(VENTANA_SEGUNDOS - transcurrido)


def registrar_intento_fallido(correo: str) -> None:
    clave = correo.lower()
    with _lock:
        cantidad, primer_fallo = _intentos.get(clave, (0, time.time()))
        if time.time() - primer_fallo >= VENTANA_SEGUNDOS:
            cantidad, primer_fallo = 0, time.time()
        _intentos[clave] = (cantidad + 1, primer_fallo)


def limpiar_intentos(correo: str) -> None:
    """Se llama cuando el login es exitoso, para no penalizar a alguien que
    solo se equivocó una vez y luego acertó."""
    with _lock:
        _intentos.pop(correo.lower(), None)
