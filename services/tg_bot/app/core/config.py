from enum import StrEnum
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotMode(StrEnum):
    POLLING = "polling"
    WEBHOOK = "webhook"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    bot_token: str

    bot_mode: BotMode = BotMode.POLLING

    webhook_url: str | None = None
    webhook_path: str = "/webhook/telegram"
    webhook_secret: str | None = None

    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8443
    
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    mongo_uri: str = "mongodb://mongodb:27017/"
    mongo_db_name: str = "telegram_bot"
    
    game_service_url: str = "http://game_service:8000"

    @property
    def webhook_full_url(self) -> str | None:
        if self.webhook_url:
            return f"{self.webhook_url}{self.webhook_path}"
        return None


settings = Settings()