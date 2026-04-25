"""Configuration applicative."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "CESOC API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./cesoc_mvp.db"
    default_session_limit_minutes: int = 60
    default_daily_print_quota: int = 10
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> list[str]:
        """Retourne les origines CORS autorisees."""
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Retourne une instance cachee des settings."""
    return Settings()
