git commit -m "feat: configurar microservicio FastAPI con PostGIS (#25)# ms-localizacion

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
└── routers/        # Endpoints HTTP
migrations/         # DDL SQL
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio |
| GET | `/mapa/puntos` | Puntos cercanos a coordenada (`lat`, `lng`, `radio`) |

## Variables de entorno

Ver `.env.example`.

## Levantar con Docker

```bash
cp .env.example .env
docker compose up --build -d
```
