"""
Pruebas unitarias — Issue #27
Actualizar punto de interés desde evento RabbitMQ

Criterios de aceptación:
- mascota.reporte.actualizado actualiza coordenadas
- mascota.reporte.estado_cambiado desactiva el punto si estado es RESUELTO u OCULTO
- mascota.reporte.eliminado elimina el punto
"""
import pytest
from tests.conftest import make_localizacion


class TestActualizarDesdeEvento:

    def test_actualiza_coordenadas_cuando_reporte_existe(self, service, mock_repo):
        """Actualiza lat/lng cuando llega el evento de actualización."""
        loc = make_localizacion()
        mock_repo.buscar_por_reporte_id.return_value = loc

        service.actualizar_desde_evento(
            reporte_id="reporte-uuid-5678",
            latitud=-36.900000,
            longitud=-73.100000,
        )

        mock_repo.actualizar_coordenadas.assert_called_once_with(
            loc, -36.900000, -73.100000, None, None
        )

    def test_ignora_actualizacion_si_no_existe_localizacion(self, service, mock_repo):
        """No hace nada si el reporte no tiene localización registrada."""
        mock_repo.buscar_por_reporte_id.return_value = None

        service.actualizar_desde_evento(
            reporte_id="reporte-uuid-5678",
            latitud=-36.900000,
            longitud=-73.100000,
        )

        mock_repo.actualizar_coordenadas.assert_not_called()

    def test_descarta_actualizacion_con_coordenadas_invalidas(self, service, mock_repo):
        """Descarta la actualización si las coordenadas son inválidas."""
        service.actualizar_desde_evento(
            reporte_id="reporte-uuid-5678",
            latitud=None,
            longitud=None,
        )

        mock_repo.actualizar_coordenadas.assert_not_called()


class TestCambiarEstadoDesdeEvento:

    def test_desactiva_punto_si_estado_es_resuelto(self, service, mock_repo):
        """Desactiva la localización cuando el estado cambia a RESUELTO."""
        loc = make_localizacion()
        mock_repo.buscar_por_reporte_id.return_value = loc

        service.cambiar_estado_desde_evento(
            reporte_id="reporte-uuid-5678",
            estado="RESUELTO",
        )

        mock_repo.actualizar_estado.assert_called_once_with(loc, "RESUELTO")

    def test_desactiva_punto_si_estado_es_oculto(self, service, mock_repo):
        """Desactiva la localización cuando el estado cambia a OCULTO."""
        loc = make_localizacion()
        mock_repo.buscar_por_reporte_id.return_value = loc

        service.cambiar_estado_desde_evento(
            reporte_id="reporte-uuid-5678",
            estado="OCULTO",
        )

        mock_repo.actualizar_estado.assert_called_once_with(loc, "OCULTO")

    def test_ignora_cambio_estado_si_no_existe_localizacion(self, service, mock_repo):
        """No hace nada si el reporte no tiene localización."""
        mock_repo.buscar_por_reporte_id.return_value = None

        service.cambiar_estado_desde_evento(
            reporte_id="reporte-uuid-5678",
            estado="RESUELTO",
        )

        mock_repo.actualizar_estado.assert_not_called()


class TestEliminarDesdeEvento:

    def test_elimina_localizacion_cuando_reporte_existe(self, service, mock_repo):
        """Elimina la localización cuando llega el evento de eliminación."""
        loc = make_localizacion()
        mock_repo.buscar_por_reporte_id.return_value = loc

        service.eliminar_desde_evento(reporte_id="reporte-uuid-5678")

        mock_repo.eliminar.assert_called_once_with(loc)

    def test_ignora_eliminacion_si_no_existe_localizacion(self, service, mock_repo):
        """No hace nada si el reporte no tiene localización registrada."""
        mock_repo.buscar_por_reporte_id.return_value = None

        service.eliminar_desde_evento(reporte_id="reporte-uuid-5678")

        mock_repo.eliminar.assert_not_called()
