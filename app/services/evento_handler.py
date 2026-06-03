import json
import logging

from aio_pika.abc import AbstractIncomingMessage

from app.config.database import SessionLocal
from app.services.localizacion_service import LocalizacionService
from app.services.mensajeria_service import EVENTOS

logger = logging.getLogger(__name__)


async def handle_evento(message: AbstractIncomingMessage) -> None:
    async with message.process(requeue=False):
        routing_key = message.routing_key
        try:
            payload = json.loads(message.body.decode())
        except json.JSONDecodeError:
            logger.error("[RabbitMQ] Mensaje no es JSON válido — descartando")
            return

        logger.info("[RabbitMQ] Evento recibido: %s", routing_key)

        if routing_key == EVENTOS["REPORTE_CREADO"]:
            await _handle_reporte_creado(payload)

        elif routing_key == EVENTOS["REPORTE_ACTUALIZADO"]:
            await _handle_reporte_actualizado(payload)

        elif routing_key == EVENTOS["REPORTE_ESTADO_CAMBIADO"]:
            await _handle_estado_cambiado(payload)

        elif routing_key == EVENTOS["REPORTE_ELIMINADO"]:
            await _handle_reporte_eliminado(payload)


async def _handle_reporte_creado(payload: dict) -> None:
    reporte_id = payload.get("reporteId")
    if not reporte_id:
        logger.error("[Evento] Payload sin reporteId — descartando: %s", payload)
        return

    db = SessionLocal()
    try:
        service = LocalizacionService(db)
        service.registrar_desde_evento(
            reporte_id=reporte_id,
            tipo_reporte=payload.get("tipo", ""),
            latitud=payload.get("ubicacionLatitud"),
            longitud=payload.get("ubicacionLongitud"),
            nombre_mascota=payload.get("nombreMascota"),
            descripcion_lugar=payload.get("direccionReferencia"),
        )
    except Exception:
        logger.exception("[Evento] Error procesando REPORTE_CREADO para %s", reporte_id)
    finally:
        db.close()


async def _handle_reporte_actualizado(payload: dict) -> None:
    reporte_id = payload.get("reporteId")
    if not reporte_id:
        logger.error("[Evento] Payload sin reporteId — descartando: %s", payload)
        return

    db = SessionLocal()
    try:
        service = LocalizacionService(db)
        service.actualizar_desde_evento(
            reporte_id=reporte_id,
            latitud=payload.get("ubicacionLatitud"),
            longitud=payload.get("ubicacionLongitud"),
            nombre_mascota=payload.get("nombreMascota"),
            descripcion_lugar=payload.get("direccionReferencia"),
        )
    except Exception:
        logger.exception("[Evento] Error procesando REPORTE_ACTUALIZADO para %s", reporte_id)
    finally:
        db.close()


async def _handle_estado_cambiado(payload: dict) -> None:
    reporte_id = payload.get("reporteId")
    estado = payload.get("estado")

    if not reporte_id or not estado:
        logger.error("[Evento] Payload inválido en ESTADO_CAMBIADO — descartando: %s", payload)
        return

    db = SessionLocal()
    try:
        service = LocalizacionService(db)
        service.cambiar_estado_desde_evento(reporte_id=reporte_id, estado=estado)
    except Exception:
        logger.exception("[Evento] Error procesando REPORTE_ESTADO_CAMBIADO para %s", reporte_id)
    finally:
        db.close()


async def _handle_reporte_eliminado(payload: dict) -> None:
    reporte_id = payload.get("reporteId")
    if not reporte_id:
        logger.error("[Evento] Payload sin reporteId — descartando: %s", payload)
        return

    db = SessionLocal()
    try:
        service = LocalizacionService(db)
        service.eliminar_desde_evento(reporte_id=reporte_id)
    except Exception:
        logger.exception("[Evento] Error procesando REPORTE_ELIMINADO para %s", reporte_id)
    finally:
        db.close()
