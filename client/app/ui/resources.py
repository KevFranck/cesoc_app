"""Ressources graphiques partagees du client desktop."""

from pathlib import Path

from PySide6.QtGui import QIcon


ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS_DIR / "cesoc_logo.svg"


def get_app_icon() -> QIcon:
    """Retourne l'icone principale de l'application."""
    return QIcon(str(LOGO_PATH))
