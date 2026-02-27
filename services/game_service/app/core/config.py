from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    environment: str = "development"
    
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/game_service"
    db_echo: bool = False
    
    redis_url: str = "redis://localhost:6379"
    
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    
    sentry_dsn: Optional[str] = None
    sentry_traces_sample_rate: float = 0.1
    sentry_profiles_sample_rate: float = 0.1
    
    max_players_per_game: int = 12
    min_player_per_game: int = 2
    game_start_timeout_seconds: int = 120
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"


settings = Settings()