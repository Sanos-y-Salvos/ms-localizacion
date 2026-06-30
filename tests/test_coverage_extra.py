"""Pruebas adicionales para alcanzar 100% de cobertura en ms-localizacion."""
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import app.config.database as _db_module


# ── config/database.py ────────────────────────────────────────────────────────

class TestDatabase:
    def setup_method(self):
        _db_module._engine = None
        _db_module._SessionLocal = None

    def teardown_method(self):
        _db_module._engine = None
        _db_module._SessionLocal = None

    def test_get_engine_crea_engine_en_primer_llamado(self):
        mock_engine = MagicMock()
        with patch("app.config.database.create_engine", return_value=mock_engine):
            from app.config.database import get_engine
            result = get_engine()
        assert result is mock_engine

    def test_get_engine_reutiliza_instancia_existente(self):
        mock_engine = MagicMock()
        with patch("app.config.database.create_engine", return_value=mock_engine) as mock_ce:
            from app.config.database import get_engine
            get_engine()
            get_engine()
        mock_ce.assert_called_once()

    def test_get_session_local_crea_sessionmaker(self):
        mock_engine = MagicMock()
        mock_sl = MagicMock()
        with patch("app.config.database.get_engine", return_value=mock_engine), \
             patch("app.config.database.sessionmaker", return_value=mock_sl):
            from app.config.database import get_session_local
            result = get_session_local()
        assert result is mock_sl

    def test_get_db_yield_y_cierra_sesion(self):
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        with patch("app.config.database.get_session_local", return_value=mock_factory):
            from app.config.database import get_db
            for db in get_db():
                assert db is mock_session
        mock_session.close.assert_called_once()

    def test_verificar_conexion_ejecuta_select_1(self):
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

        with patch("app.config.database.get_engine", return_value=mock_engine):
            from app.config.database import verificar_conexion
            verificar_conexion()

        mock_conn.execute.assert_called_once()


# ── repositories/localizacion_repository.py ──────────────────────────────────

class TestLocalizacionRepository:
    def test_init_asigna_db(self):
        from app.repositories.localizacion_repository import LocalizacionRepository
        db = MagicMock()
        repo = LocalizacionRepository(db)
        assert repo.db is db

    def test_crear_agrega_y_persiste(self):
        from app.repositories.localizacion_repository import LocalizacionRepository
        db = MagicMock()
        repo = LocalizacionRepository(db)
        mock_loc = MagicMock()

        with patch("app.repositories.localizacion_repository.ST_SetSRID"), \
             patch("app.repositories.localizacion_repository.ST_MakePoint"), \
             patch("app.repositories.localizacion_repository.Localizacion",
                   return_value=mock_loc):
            result = repo.crear(
                reporte_id="r1",
                tipo_reporte="PERDIDA",
                latitud=-36.827,
                longitud=-73.049,
            )

        db.add.assert_called_once_with(mock_loc)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(mock_loc)
        assert result is mock_loc

    def test_buscar_por_reporte_id_retorna_resultado(self):
        from app.repositories.localizacion_repository import LocalizacionRepository
        db = MagicMock()
        repo = LocalizacionRepository(db)
        expected = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = expected

        result = repo.buscar_por_reporte_id("r1")
        assert result is expected

    def test_buscar_en_radio_retorna_lista(self):
        from app.repositories.localizacion_repository import LocalizacionRepository
        db = MagicMock()
        repo = LocalizacionRepository(db)
        expected = [MagicMock()]
        db.query.return_value.filter.return_value.limit.return_value.all.return_value = expected

        with patch("app.repositories.localizacion_repository.ST_SetSRID"), \
             patch("app.repositories.localizacion_repository.ST_MakePoint"), \
             patch("app.repositories.localizacion_repository.ST_DWithin"):
            result = repo.buscar_en_radio(-36.827, -73.049, 5000)

        assert result is expected

    def test_actualizar_coordenadas_actualiza_atributos(self):
        from app.repositories.localizacion_repository import LocalizacionRepository
        db = MagicMock()
        repo = LocalizacionRepository(db)
        loc = MagicMock()

        with patch("app.repositories.localizacion_repository.ST_SetSRID"), \
             patch("app.repositories.localizacion_repository.ST_MakePoint"):
            repo.actualizar_coordenadas(loc, -36.9, -73.1, "Firulais", "Un perro")

        assert loc.latitud == -36.9
        assert loc.longitud == -73.1
        assert loc.nombre_mascota == "Firulais"
        assert loc.descripcion == "Un perro"
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(loc)

    def test_actualizar_coordenadas_sin_opcionales(self):
        from app.repositories.localizacion_repository import LocalizacionRepository
        db = MagicMock()
        repo = LocalizacionRepository(db)
        loc = MagicMock()
        original_nombre = loc.nombre_mascota

        with patch("app.repositories.localizacion_repository.ST_SetSRID"), \
             patch("app.repositories.localizacion_repository.ST_MakePoint"):
            repo.actualizar_coordenadas(loc, -36.9, -73.1)

        # nombre_mascota and descripcion must NOT be reassigned
        assert loc.nombre_mascota is original_nombre
        db.commit.assert_called_once()

    def test_actualizar_estado_resuelto_desactiva(self):
        from app.repositories.localizacion_repository import LocalizacionRepository
        db = MagicMock()
        repo = LocalizacionRepository(db)
        loc = MagicMock()
        repo.actualizar_estado(loc, "RESUELTO")
        assert loc.estado_reporte == "RESUELTO"
        assert loc.activo == False
        db.commit.assert_called_once()

    def test_actualizar_estado_en_busqueda_activa(self):
        from app.repositories.localizacion_repository import LocalizacionRepository
        db = MagicMock()
        repo = LocalizacionRepository(db)
        loc = MagicMock()
        repo.actualizar_estado(loc, "EN_BUSQUEDA")
        assert loc.activo == True

    def test_eliminar_borra_y_hace_commit(self):
        from app.repositories.localizacion_repository import LocalizacionRepository
        db = MagicMock()
        repo = LocalizacionRepository(db)
        loc = MagicMock()
        repo.eliminar(loc)
        db.delete.assert_called_once_with(loc)
        db.commit.assert_called_once()


# ── services/localizacion_service.py (líneas 13 y 80) ────────────────────────

class TestLocalizacionServiceInit:
    def test_init_asigna_repo(self):
        from app.services.localizacion_service import LocalizacionService
        db = MagicMock()
        with patch("app.services.localizacion_service.LocalizacionRepository") as mock_lr:
            svc = LocalizacionService(db)
        mock_lr.assert_called_once_with(db)
        assert svc.repo is mock_lr.return_value


class TestCambiarEstadoElseBranch:
    def test_estado_en_busqueda_cubre_rama_else(self):
        from app.services.localizacion_service import LocalizacionService
        svc = LocalizacionService.__new__(LocalizacionService)
        mock_repo = MagicMock()
        svc.repo = mock_repo
        loc = MagicMock()
        mock_repo.buscar_por_reporte_id.return_value = loc

        svc.cambiar_estado_desde_evento(reporte_id="r1", estado="EN_BUSQUEDA")

        mock_repo.actualizar_estado.assert_called_once_with(loc, "EN_BUSQUEDA")


# ── services/evento_handler.py ────────────────────────────────────────────────

def _make_message(routing_key: str, body_dict: dict) -> MagicMock:
    """Crea un mensaje RabbitMQ mock con async context manager."""
    msg = MagicMock()
    msg.routing_key = routing_key
    msg.body = json.dumps(body_dict).encode()
    msg.process.return_value = AsyncMock()
    return msg


class TestHandleEvento:
    def test_json_invalido_descarta_silenciosamente(self):
        async def _run():
            from app.services.evento_handler import handle_evento
            msg = MagicMock()
            msg.routing_key = "mascota.reporte.creado"
            msg.body = b"no-es-json"
            msg.process.return_value = AsyncMock()
            await handle_evento(msg)

        asyncio.run(_run())

    def test_rutea_reporte_creado(self):
        async def _run():
            from app.services.evento_handler import handle_evento
            msg = _make_message(
                "mascota.reporte.creado",
                {"reporteId": "r1", "tipo": "PERDIDA",
                 "ubicacionLatitud": -36.8, "ubicacionLongitud": -73.0},
            )
            mock_db = MagicMock()
            mock_service = MagicMock()
            mock_factory = MagicMock(return_value=mock_db)
            with patch("app.services.evento_handler.get_session_local",
                       return_value=mock_factory), \
                 patch("app.services.evento_handler.LocalizacionService",
                       return_value=mock_service):
                await handle_evento(msg)
            mock_service.registrar_desde_evento.assert_called_once()
            mock_db.close.assert_called_once()

        asyncio.run(_run())

    def test_rutea_reporte_actualizado(self):
        async def _run():
            from app.services.evento_handler import handle_evento
            msg = _make_message(
                "mascota.reporte.actualizado",
                {"reporteId": "r1", "ubicacionLatitud": -36.8, "ubicacionLongitud": -73.0},
            )
            mock_db = MagicMock()
            mock_service = MagicMock()
            with patch("app.services.evento_handler.get_session_local",
                       return_value=MagicMock(return_value=mock_db)), \
                 patch("app.services.evento_handler.LocalizacionService",
                       return_value=mock_service):
                await handle_evento(msg)
            mock_service.actualizar_desde_evento.assert_called_once()

        asyncio.run(_run())

    def test_rutea_estado_cambiado(self):
        async def _run():
            from app.services.evento_handler import handle_evento
            msg = _make_message(
                "mascota.reporte.estado_cambiado",
                {"reporteId": "r1", "estado": "RESUELTO"},
            )
            mock_db = MagicMock()
            mock_service = MagicMock()
            with patch("app.services.evento_handler.get_session_local",
                       return_value=MagicMock(return_value=mock_db)), \
                 patch("app.services.evento_handler.LocalizacionService",
                       return_value=mock_service):
                await handle_evento(msg)
            mock_service.cambiar_estado_desde_evento.assert_called_once()

        asyncio.run(_run())

    def test_rutea_reporte_eliminado(self):
        async def _run():
            from app.services.evento_handler import handle_evento
            msg = _make_message(
                "mascota.reporte.eliminado",
                {"reporteId": "r1"},
            )
            mock_db = MagicMock()
            mock_service = MagicMock()
            with patch("app.services.evento_handler.get_session_local",
                       return_value=MagicMock(return_value=mock_db)), \
                 patch("app.services.evento_handler.LocalizacionService",
                       return_value=mock_service):
                await handle_evento(msg)
            mock_service.eliminar_desde_evento.assert_called_once()

        asyncio.run(_run())


class TestHandleReporteCreado:
    def test_sin_reporte_id_retorna_sin_hacer_nada(self):
        async def _run():
            from app.services.evento_handler import _handle_reporte_creado
            await _handle_reporte_creado({})

        asyncio.run(_run())

    def test_excepcion_en_service_no_propaga_y_cierra_db(self):
        async def _run():
            from app.services.evento_handler import _handle_reporte_creado
            mock_db = MagicMock()
            with patch("app.services.evento_handler.get_session_local",
                       return_value=MagicMock(return_value=mock_db)), \
                 patch("app.services.evento_handler.LocalizacionService",
                       side_effect=Exception("fallo")):
                await _handle_reporte_creado({"reporteId": "r1"})
            mock_db.close.assert_called_once()

        asyncio.run(_run())


class TestHandleReporteActualizado:
    def test_sin_reporte_id_retorna_sin_hacer_nada(self):
        async def _run():
            from app.services.evento_handler import _handle_reporte_actualizado
            await _handle_reporte_actualizado({})

        asyncio.run(_run())

    def test_excepcion_no_propaga_y_cierra_db(self):
        async def _run():
            from app.services.evento_handler import _handle_reporte_actualizado
            mock_db = MagicMock()
            with patch("app.services.evento_handler.get_session_local",
                       return_value=MagicMock(return_value=mock_db)), \
                 patch("app.services.evento_handler.LocalizacionService",
                       side_effect=Exception("fallo")):
                await _handle_reporte_actualizado({"reporteId": "r1"})
            mock_db.close.assert_called_once()

        asyncio.run(_run())


class TestHandleEstadoCambiado:
    def test_payload_invalido_retorna_sin_hacer_nada(self):
        async def _run():
            from app.services.evento_handler import _handle_estado_cambiado
            await _handle_estado_cambiado({})
            await _handle_estado_cambiado({"reporteId": "r1"})
            await _handle_estado_cambiado({"estado": "RESUELTO"})

        asyncio.run(_run())

    def test_excepcion_no_propaga_y_cierra_db(self):
        async def _run():
            from app.services.evento_handler import _handle_estado_cambiado
            mock_db = MagicMock()
            with patch("app.services.evento_handler.get_session_local",
                       return_value=MagicMock(return_value=mock_db)), \
                 patch("app.services.evento_handler.LocalizacionService",
                       side_effect=Exception("fallo")):
                await _handle_estado_cambiado({"reporteId": "r1", "estado": "RESUELTO"})
            mock_db.close.assert_called_once()

        asyncio.run(_run())


class TestHandleReporteEliminado:
    def test_sin_reporte_id_retorna_sin_hacer_nada(self):
        async def _run():
            from app.services.evento_handler import _handle_reporte_eliminado
            await _handle_reporte_eliminado({})

        asyncio.run(_run())

    def test_excepcion_no_propaga_y_cierra_db(self):
        async def _run():
            from app.services.evento_handler import _handle_reporte_eliminado
            mock_db = MagicMock()
            with patch("app.services.evento_handler.get_session_local",
                       return_value=MagicMock(return_value=mock_db)), \
                 patch("app.services.evento_handler.LocalizacionService",
                       side_effect=Exception("fallo")):
                await _handle_reporte_eliminado({"reporteId": "r1"})
            mock_db.close.assert_called_once()

        asyncio.run(_run())


# ── services/mensajeria_service.py ───────────────────────────────────────────

class TestLocalizacionMensajeria:
    def test_conectar_establece_connection_y_channel(self):
        from app.services.mensajeria_service import MensajeriaService
        svc = MensajeriaService()
        mock_channel = AsyncMock()
        mock_connection = AsyncMock()
        mock_connection.channel.return_value = mock_channel

        async def _run():
            with patch("app.services.mensajeria_service.aio_pika.connect_robust",
                       AsyncMock(return_value=mock_connection)):
                await svc.conectar()

        asyncio.run(_run())
        assert svc._connection is mock_connection
        assert svc._channel is mock_channel
        assert svc._intentos == 0
        mock_channel.declare_exchange.assert_awaited_once()

    def test_iniciar_consumo_sin_channel_lanza_error(self):
        from app.services.mensajeria_service import MensajeriaService
        svc = MensajeriaService()
        svc._channel = None
        with pytest.raises(RuntimeError):
            asyncio.run(svc.iniciar_consumo(MagicMock()))

    def test_iniciar_consumo_declara_cola_y_binds(self):
        from app.services.mensajeria_service import MensajeriaService, EVENTOS
        svc = MensajeriaService()
        mock_exchange = AsyncMock()
        mock_queue = AsyncMock()
        mock_channel = AsyncMock()
        mock_channel.get_exchange.return_value = mock_exchange
        mock_channel.declare_queue.return_value = mock_queue
        svc._channel = mock_channel
        handler = MagicMock()
        asyncio.run(svc.iniciar_consumo(handler))
        assert mock_queue.bind.await_count == len(EVENTOS)
        mock_queue.consume.assert_awaited_once_with(handler)

    def test_conectar_con_reintento_exito_primer_intento(self):
        from app.services.mensajeria_service import MensajeriaService
        svc = MensajeriaService()
        handler = MagicMock()
        with patch.object(svc, "conectar", AsyncMock()), \
             patch.object(svc, "iniciar_consumo", AsyncMock()):
            asyncio.run(svc.conectar_con_reintento(handler))

    def test_conectar_con_reintento_agota_intentos(self):
        from app.services.mensajeria_service import MensajeriaService
        svc = MensajeriaService()
        with patch.object(svc, "conectar", AsyncMock(side_effect=Exception("down"))), \
             patch("app.services.mensajeria_service.asyncio.sleep", AsyncMock()):
            asyncio.run(svc.conectar_con_reintento(MagicMock()))

    def test_cerrar_cierra_conexion_si_existe(self):
        from app.services.mensajeria_service import MensajeriaService
        svc = MensajeriaService()
        mock_conn = AsyncMock()
        svc._connection = mock_conn
        asyncio.run(svc.cerrar())
        mock_conn.close.assert_awaited_once()

    def test_cerrar_sin_conexion_no_lanza(self):
        from app.services.mensajeria_service import MensajeriaService
        svc = MensajeriaService()
        svc._connection = None
        asyncio.run(svc.cerrar())


# ── routers/mapa.py ───────────────────────────────────────────────────────────

def _make_loc_mock(**kwargs):
    loc = MagicMock()
    loc.id = kwargs.get("id", "uuid-1")
    loc.reporte_id = kwargs.get("reporte_id", "r1")
    loc.tipo_reporte = kwargs.get("tipo_reporte", "PERDIDA")
    loc.nombre_mascota = kwargs.get("nombre_mascota", "Firulais")
    loc.especie = kwargs.get("especie", "perro")
    loc.latitud = kwargs.get("latitud", -36.826992)
    loc.longitud = kwargs.get("longitud", -73.049771)
    loc.direccion_aproximada = kwargs.get("direccion_aproximada", None)
    loc.descripcion = kwargs.get("descripcion", None)
    loc.codigo_chip = kwargs.get("codigo_chip", None)
    loc.foto_url = kwargs.get("foto_url", None)
    return loc


class TestMapaRouter:
    def test_from_orm_safe_construye_punto_mapa(self):
        from app.routers.mapa import PuntoMapa
        obj = _make_loc_mock()
        punto = PuntoMapa.from_orm_safe(obj)
        assert punto.id == "uuid-1"
        assert punto.reporte_id == "r1"
        assert punto.latitud == -36.826992

    def test_obtener_puntos_retorna_lista(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.config.database import get_db
        from app.routers.mapa import router

        test_app = FastAPI()
        test_app.include_router(router)

        loc = _make_loc_mock()
        mock_service = MagicMock()
        mock_service.buscar_en_radio.return_value = [loc]

        def override_db():
            yield MagicMock()

        test_app.dependency_overrides[get_db] = override_db

        with patch("app.routers.mapa.LocalizacionService", return_value=mock_service):
            client = TestClient(test_app)
            response = client.get("/mapa/puntos?lat=-36.827&lng=-73.049&radio=5000")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["reporte_id"] == "r1"

    def test_obtener_todos_los_puntos_retorna_lista(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.config.database import get_db
        from app.routers.mapa import router

        test_app = FastAPI()
        test_app.include_router(router)

        loc = _make_loc_mock(id="uuid-2", reporte_id="r2")

        def override_db():
            db = MagicMock()
            db.query.return_value.filter.return_value.all.return_value = [loc]
            yield db

        test_app.dependency_overrides[get_db] = override_db

        client = TestClient(test_app)
        response = client.get("/mapa/puntos/todos")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["reporte_id"] == "r2"


# ── app/main.py ───────────────────────────────────────────────────────────────

class TestMain:
    def test_app_tiene_titulo_correcto(self):
        from app.main import app
        assert app.title == "ms-localizacion"

    def test_lifespan_llama_verificar_conexion_y_cerrar(self):
        mock_ms = MagicMock()
        mock_ms.cerrar = AsyncMock()

        def fake_create_task(coro):
            if hasattr(coro, "close"):
                coro.close()
            return MagicMock()

        async def _run():
            from app.main import lifespan, app as loc_app
            with patch("app.main.verificar_conexion") as mock_vc, \
                 patch("app.main.mensajeria_service", mock_ms), \
                 patch("app.main.asyncio.create_task", side_effect=fake_create_task):
                async with lifespan(loc_app):
                    pass
            mock_vc.assert_called_once()
            mock_ms.cerrar.assert_awaited_once()

        asyncio.run(_run())
