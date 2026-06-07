"""
Pruebas unitarias — Issue #25
Configurar microservicio FastAPI con PostGIS

Criterios de aceptación verificables con pruebas unitarias:
- Health check responde en GET /health
- Configuracion carga correctamente las variables de entorno
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestHealthCheck:

    def test_health_responde_200(self):
        """GET /health retorna status 200."""
        with patch("app.config.database.verificar_conexion"), \
             patch("app.services.mensajeria_service.MensajeriaService.conectar_con_reintento"):
            from app.main import app
            client = TestClient(app)
            response = client.get("/health")
            assert response.status_code == 200

    def test_health_retorna_campos_esperados(self):
        """GET /health retorna status, microservicio y version."""
        with patch("app.config.database.verificar_conexion"), \
             patch("app.services.mensajeria_service.MensajeriaService.conectar_con_reintento"):
            from app.main import app
            client = TestClient(app)
            response = client.get("/health")
            data = response.json()
            assert data["status"] == "ok"
            assert data["microservicio"] == "ms-localizacion"
            assert "version" in data


class TestSettings:

    def test_database_url_se_construye_correctamente(self):
        """La URL de BD se arma correctamente desde las variables de entorno."""
        from app.config.settings import Settings
        s = Settings(
            db_user="usuario",
            db_password="clave",
            db_host="localhost",
            db_port=5432,
            db_name="mi_bd",
        )
        assert s.database_url == "postgresql+psycopg2://usuario:clave@localhost:5432/mi_bd"

    def test_settings_tiene_valores_por_defecto(self):
        """Settings tiene valores por defecto para todas las variables."""
        from app.config.settings import Settings
        s = Settings()
        assert s.db_host == "localhost"
        assert s.db_port == 5432
        assert s.rabbitmq_exchange == "sanos_y_salvos_events"
