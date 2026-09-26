"""Helpers de Wompi sin dependencias externas (mismo criterio que
app/core/email.py con Resend): solo hashlib/hmac de la librería estándar,
para no agregar un cliente HTTP nuevo a requirements.txt. El backend nunca
llama a la API de Wompi directamente: el cliente paga en el Web Checkout
(un widget que Wompi aloja) y Wompi nos avisa el resultado por webhook."""

import hashlib
import hmac
import secrets

from app.core.config import settings


def generar_referencia(id_solicitud: int) -> str:
    """Referencia única por intento de cobro. Se puede regenerar (ver
    crud_pago.regenerar_referencia) si un intento anterior quedó declinado
    o con error, para permitir que el cliente vuelva a intentar."""
    return f"VP-{id_solicitud}-{secrets.token_hex(4)}"


def monto_en_centavos(monto: float) -> int:
    """Wompi siempre trabaja en centavos (COP sin decimales reales, pero la
    API igual espera *100)."""
    return int(round(monto * 100))


def firma_integridad(*, referencia: str, monto_en_centavos: int, moneda: str) -> str:
    """SHA-256 de referencia+monto+moneda+secreto, tal como lo exige Wompi
    para el Web Checkout (evita que alguien manipule el monto desde el
    navegador antes de abrir el widget)."""
    cadena = f"{referencia}{monto_en_centavos}{moneda}{settings.wompi_secreto_integridad}"
    return hashlib.sha256(cadena.encode("utf-8")).hexdigest()


def _valor_anidado(datos: dict, ruta: str):
    valor = datos
    for parte in ruta.split("."):
        if not isinstance(valor, dict):
            return None
        valor = valor.get(parte)
    return valor


def verificar_firma_evento(payload: dict) -> bool:
    """Valida la firma que Wompi manda en cada webhook: sha256 de los
    valores de las propiedades que indica signature.properties (en el
    orden dado), más el timestamp del evento, más el secreto de eventos.
    Si no coincide, el webhook se ignora (podría ser de otra cuenta o un
    intento de falsificarlo)."""
    firma = payload.get("signature") or {}
    propiedades = firma.get("properties") or []
    checksum_recibido = str(firma.get("checksum") or "")
    timestamp = str(payload.get("timestamp") or "")
    datos = payload.get("data") or {}

    if not propiedades or not checksum_recibido:
        return False

    cadena = "".join(str(_valor_anidado(datos, ruta) or "") for ruta in propiedades)
    cadena += f"{timestamp}{settings.wompi_secreto_eventos}"
    checksum_calculado = hashlib.sha256(cadena.encode("utf-8")).hexdigest()
    return hmac.compare_digest(checksum_calculado, checksum_recibido.lower())
