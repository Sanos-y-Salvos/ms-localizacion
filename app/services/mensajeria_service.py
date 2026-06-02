"""
MensajeriaService — consumidor RabbitMQ.

Por ahora solo establece la conexión y declara el exchange.
Los handlers de eventos se añaden en las issues #26 y #27.
"""
import asyncio
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.config.settings import settings

logger = logging.getLogger(__name__)

EVENTOS = {
    "REPORTE_CREADO":          "mascota.reporte.creado",
    "REPORTE_ACTUALIZADO":     "mascota.reporte.actualizado",
    "REPORTE_ESTADO_CAMBIADO": "mascota.reporte.estado_cambiado",
    "REPORTE_ELIMINADO":       "mascota.reporte.eliminado",
}

QUEUE_NAME = "localizacion.eventos"
REINTENTOS_MAX = 10
ESPERA_BASE_SEG = 2


class MensajeriaService:
    def __init__(self):
        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._intentos = 0

    async def conectar(self) -> None:
        self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self._channel = await self._connection.channel()

        await self._channel.declare_exchange(
            settings.rabbitmq_exchange,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        self._intentos = 0
        logger.info("[RabbitMQ] Conectado — exchange: %s", settings.rabbitmq_exchange)

    async def iniciar_consumo(self, handler) -> None:
        """
        Declara la cola, enlaza los routing keys y empieza a consumir.
        El handler concreto se inyecta desde las issues #26/#27.
        """
        if not self._channel:
            raise RuntimeError("Canal RabbitMQ no inicializado")

        exchange = await self._channel.get_exchange(settings.rabbitmq_exchange)
        queue = await self._channel.declare_queue(QUEUE_NAME, durable=True)

        for routing_key in EVENTOS.values():
            await queue.bind(exchange, routing_key=routing_key)

        await queue.consume(handler)
        logger.info("[RabbitMQ] Consumidor activo en cola '%s'", QUEUE_NAME)

    async def conectar_con_reintento(self, handler) -> None:
        """
        Intenta conectar con backoff exponencial.
        Si falla, los endpoints de lectura siguen funcionando.
        """
        for intento in range(1, REINTENTOS_MAX + 1):
            try:
                await self.conectar()
                await self.iniciar_consumo(handler)
                return
            except Exception as exc:
                espera = min(ESPERA_BASE_SEG * 2 ** (intento - 1), 34)
                logger.warning(
                    "[RabbitMQ] Intento %d/%d fallido: %s — reintentando en %ds",
                    intento, REINTENTOS_MAX, exc, espera,
                )
                await asyncio.sleep(espera)

        logger.error("[RabbitMQ] No se pudo conectar tras %d intentos. Consumidor inactivo.", REINTENTOS_MAX)

    async def cerrar(self) -> None:
        if self._connection:
            await self._connection.close()


# Instancia única
mensajeria_service = MensajeriaService()
