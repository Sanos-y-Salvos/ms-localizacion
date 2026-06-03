import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import verificar_conexion
from app.config.settings import settings
from app.routers.health import router as health_router
from app.routers.mapa import router as mapa_router
from app.services.mensajeria_service import mensajeria_service
from app.services.evento_handler import handle_evento

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Base de datos — crítico
    verificar_conexion()

    # 2. RabbitMQ — no crítico: los GET funcionan aunque falle
    asyncio.create_task(
        mensajeria_service.conectar_con_reintento(handle_evento)
    )

    yield

    await mensajeria_service.cerrar()
    logger.info("[ms-localizacion] Apagado limpio")


app = FastAPI(
    title="ms-localizacion",
    description="Microservicio de geolocalización — Sanos y Salvos",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(mapa_router)
