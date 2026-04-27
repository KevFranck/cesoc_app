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


def create_workstation(db: Session, *, name: str, location: str, is_active: bool = True) -> Workstation:
    """Cree un nouveau poste."""
    workstation = Workstation(name=name, location=location, is_active=is_active)
    db.add(workstation)
    db.commit()
    db.refresh(workstation)
    return workstation


def get_by_id(db: Session, workstation_id: int) -> Workstation | None:
    """Retourne un poste par id."""
    return db.get(Workstation, workstation_id)


def save(db: Session, workstation: Workstation) -> Workstation:
    """Persist un poste mis a jour."""
    db.add(workstation)
    db.commit()
    db.refresh(workstation)
    return workstation
