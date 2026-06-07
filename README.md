# ms-localizacion

Microservicio de geolocalización del proyecto **Sanos y Salvos**.

Registra y consulta ubicaciones geográficas de reportes de mascotas perdidas o encontradas. Se comunica con `ms-mascotas` exclusivamente mediante eventos RabbitMQ — no expone endpoints de escritura.

## Stack

- **Python 3.12** + **FastAPI**
- **PostgreSQL 16** + **PostGIS 3.4**
- **RabbitMQ 3.12** (consumidor de eventos)
- **SQLAlchemy 2** + **GeoAlchemy2**
- **Docker** + **Docker Compose**

## Estructura

```
app/
├── config/         # Configuración y conexión a BD
├── models/         # Modelos SQLAlchemy
├── repositories/   # Acceso a datos
├── services/       # Lógica de negocio y consumidor RabbitMQ
└── routes/         # Endpoints HTTP
migrations/         # DDL SQL
tests/              # Pruebas unitarias
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio |
| GET | `/mapa/puntos` | Puntos cercanos a coordenada (`lat`, `lng`, `radio`) |
| GET | `/mapa/puntos/todos` | Todos los puntos activos (solo testing) |

## Variables de entorno

Ver `.env.example`.

## Levantar con Docker

Requiere que `ms-mascotas` esté corriendo primero (provee la red y RabbitMQ):

```bash
# 1. Levantar ms-mascotas
cd ../ms-mascotas
docker compose up -d

# 2. Levantar ms-localizacion
cd ../ms-localizacion
cp .env.example .env
docker compose up --build -d
```

El servicio queda disponible en `http://localhost:3004`.

Documentación interactiva: `http://localhost:3004/docs`

## Pruebas unitarias

Las pruebas no requieren Docker, PostgreSQL ni RabbitMQ — usan mocks.

### Requisitos

Python 3.12 o superior. Instalar dependencias de testing:

```bash
pip install fastapi sqlalchemy geoalchemy2 pydantic-settings pytest httpx aio-pika
```

> **Nota:** No instalar `psycopg2-binary` para correr las pruebas — no es necesario y puede fallar en algunos entornos sin PostgreSQL instalado localmente.

### Correr las pruebas

```bash
python -m pytest tests/ -v
```

Resultado esperado: **23 pruebas, 0 fallos**

```
tests/test_issue25_setup.py::TestHealthCheck::test_health_responde_200 PASSED
tests/test_issue25_setup.py::TestHealthCheck::test_health_retorna_campos_esperados PASSED
tests/test_issue25_setup.py::TestSettings::test_database_url_se_construye_correctamente PASSED
tests/test_issue25_setup.py::TestSettings::test_settings_tiene_valores_por_defecto PASSED
tests/test_issue26_registrar_punto.py::TestRegistrarDesdeEvento::test_registra_localizacion_con_datos_validos PASSED
tests/test_issue26_registrar_punto.py::TestRegistrarDesdeEvento::test_descarta_si_coordenadas_ninguna PASSED
tests/test_issue26_registrar_punto.py::TestRegistrarDesdeEvento::test_descarta_si_latitud_fuera_de_rango PASSED
tests/test_issue26_registrar_punto.py::TestRegistrarDesdeEvento::test_descarta_si_longitud_fuera_de_rango PASSED
tests/test_issue26_registrar_punto.py::TestRegistrarDesdeEvento::test_descarta_si_coordenadas_no_son_numericas PASSED
tests/test_issue26_registrar_punto.py::TestRegistrarDesdeEvento::test_idempotencia_no_duplica_localizacion PASSED
tests/test_issue27_actualizar_punto.py::TestActualizarDesdeEvento::test_actualiza_coordenadas_cuando_reporte_existe PASSED
tests/test_issue27_actualizar_punto.py::TestActualizarDesdeEvento::test_ignora_actualizacion_si_no_existe_localizacion PASSED
tests/test_issue27_actualizar_punto.py::TestActualizarDesdeEvento::test_descarta_actualizacion_con_coordenadas_invalidas PASSED
tests/test_issue27_actualizar_punto.py::TestCambiarEstadoDesdeEvento::test_desactiva_punto_si_estado_es_resuelto PASSED
tests/test_issue27_actualizar_punto.py::TestCambiarEstadoDesdeEvento::test_desactiva_punto_si_estado_es_oculto PASSED
tests/test_issue27_actualizar_punto.py::TestCambiarEstadoDesdeEvento::test_ignora_cambio_estado_si_no_existe_localizacion PASSED
tests/test_issue27_actualizar_punto.py::TestEliminarDesdeEvento::test_elimina_localizacion_cuando_reporte_existe PASSED
tests/test_issue27_actualizar_punto.py::TestEliminarDesdeEvento::test_ignora_eliminacion_si_no_existe_localizacion PASSED
tests/test_issue28_consulta_mapa.py::TestBuscarEnRadio::test_retorna_puntos_dentro_del_radio PASSED
tests/test_issue28_consulta_mapa.py::TestBuscarEnRadio::test_retorna_lista_vacia_si_no_hay_puntos PASSED
tests/test_issue28_consulta_mapa.py::TestBuscarEnRadio::test_radio_maximo_50km PASSED
tests/test_issue28_consulta_mapa.py::TestBuscarEnRadio::test_radio_exactamente_50km_es_valido PASSED
tests/test_issue28_consulta_mapa.py::TestBuscarEnRadio::test_limite_300_marcadores_se_aplica_en_repositorio PASSED
```

### Cobertura por issue

| Issue | Pruebas | Qué se verifica |
|-------|---------|-----------------|
| #25 Setup | 4 | Health check, construcción de URL de BD, valores por defecto |
| #26 Registrar | 6 | Registro válido, coordenadas inválidas, idempotencia |
| #27 Actualizar | 8 | Actualización, cambio de estado, eliminación |
| #28 Consulta | 5 | Búsqueda por radio, límite 300, radio máximo 50 km |
