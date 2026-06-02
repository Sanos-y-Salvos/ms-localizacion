from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Servidor
    port: int = 8000

    # Base de datos
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "ms_localizacion"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672"
    rabbitmq_exchange: str = "sanos_y_salvos_events"

    # CORS
    cors_origin: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
