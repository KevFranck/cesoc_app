"""Configuration cliente."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientSettings(BaseSettings):
    """Configuration du client desktop."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    client_app_name: str = "CESOC Desktop"
    client_api_base_url: str = "http://127.0.0.1:8000/api/v1"
    client_default_workstation: str = "POSTE-01"
    client_session_limit_minutes: int = 60
    client_session_warning_minutes: str = "15,5,1"
    client_browser_home_url: str = "https://www.google.com"
    client_word_executable: str = "winword.exe"
    client_workspace_root: str = str(Path.home() / "Documents" / "CESOC Sessions")
    client_print_monitor_enabled: bool = True
    client_print_monitor_interval_ms: int = 1500

    @property
    def session_warning_thresholds(self) -> list[int]:
        """Retourne les seuils d'alerte de session."""
        thresholds = []
        for value in self.client_session_warning_minutes.split(","):
            value = value.strip()
            if not value:
                continue
            try:
                parsed = int(value)
            except ValueError:
                continue
            if parsed >= 0:
                thresholds.append(parsed)
        return sorted(set(thresholds), reverse=True)


@lru_cache
def get_client_settings() -> ClientSettings:
    """Retourne les settings du client."""
    return ClientSettings()
