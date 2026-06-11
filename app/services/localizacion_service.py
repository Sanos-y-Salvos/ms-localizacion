import logging

from sqlalchemy.orm import Session

from app.repositories.localizacion_repository import LocalizacionRepository

logger = logging.getLogger(__name__)


class LocalizacionService:

    def __init__(self, db: Session):
        self.repo = LocalizacionRepository(db)

    def registrar_desde_evento(
        self,
        reporte_id: str,
        tipo_reporte: str,
        latitud: float,
        longitud: float,
        nombre_mascota: str | None = None,
        descripcion: str | None = None,
        codigo_chip: str | None = None,
        foto_url: str | None = None,
    ) -> None:
        if not _coordenadas_validas(latitud, longitud):
            logger.error("[Evento] Coordenadas invalidas para reporte %s. Descartando.", reporte_id)
            return

        existente = self.repo.buscar_por_reporte_id(reporte_id)
        if existente:
            logger.debug("[Evento] Reporte %s ya tiene localizacion. Ignorando.", reporte_id)
            return

        self.repo.crear(
            reporte_id=reporte_id,
            tipo_reporte=tipo_reporte,
            latitud=latitud,
            longitud=longitud,
            nombre_mascota=nombre_mascota,
            descripcion=descripcion,
            codigo_chip=codigo_chip,
            foto_url=foto_url,
        )
        logger.info("[Evento] Localizacion registrada para reporte %s", reporte_id)

    def actualizar_desde_evento(
        self,
        reporte_id: str,
        latitud: float,
        longitud: float,
        nombre_mascota: str | None = None,
        descripcion: str | None = None,
    ) -> None:
        if not _coordenadas_validas(latitud, longitud):
            logger.error("[Evento] Coordenadas invalidas en actualizacion de reporte %s. Descartando.", reporte_id)
            return

        loc = self.repo.buscar_por_reporte_id(reporte_id)
        if not loc:
            logger.warning("[Evento] Reporte %s no tiene localizacion registrada. Ignorando.", reporte_id)
            return

        self.repo.actualizar_coordenadas(loc, latitud, longitud, nombre_mascota, descripcion)
        logger.info("[Evento] Localizacion actualizada para reporte %s", reporte_id)

    def cambiar_estado_desde_evento(self, reporte_id: str, estado: str) -> None:
        loc = self.repo.buscar_por_reporte_id(reporte_id)
        if not loc:
            logger.warning("[Evento] Reporte %s no tiene localizacion registrada. Ignorando.", reporte_id)
            return

        self.repo.actualizar_estado(loc, estado)

        if estado in ("RESUELTO", "OCULTO", "ABANDONADO"):
            logger.info("[Evento] Localizacion desactivada para reporte %s (estado: %s)", reporte_id, estado)
        else:
            logger.info("[Evento] Estado actualizado a %s para reporte %s", estado, reporte_id)

    def eliminar_desde_evento(self, reporte_id: str) -> None:
        loc = self.repo.buscar_por_reporte_id(reporte_id)
        if not loc:
            logger.warning("[Evento] Reporte %s no tiene localizacion. Ignorando.", reporte_id)
            return

        self.repo.eliminar(loc)
        logger.info("[Evento] Localizacion eliminada para reporte %s", reporte_id)

    def buscar_en_radio(
        self,
        latitud: float,
        longitud: float,
        radio_metros: float,
    ) -> list:
        if radio_metros > 50_000:
            raise ValueError("El radio maximo de busqueda es 50 km")
        return self.repo.buscar_en_radio(latitud, longitud, radio_metros)


def _coordenadas_validas(latitud: float, longitud: float) -> bool:
    return (
        isinstance(latitud, (int, float))
        and isinstance(longitud, (int, float))
        and -90 <= latitud <= 90
        and -180 <= longitud <= 180
    )
