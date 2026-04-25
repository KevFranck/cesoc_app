"""Acces aux postes."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from server.app.models import Workstation


def get_by_name(db: Session, name: str) -> Workstation | None:
    """Retourne un poste par son nom."""
    return db.scalar(select(Workstation).where(Workstation.name == name))


def list_workstations(db: Session) -> list[Workstation]:
    """Retourne tous les postes."""
    return list(db.scalars(select(Workstation).order_by(Workstation.id)))
