"""Acces aux utilisateurs."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from server.app.models import User


def get_by_external_id(db: Session, external_id: str) -> User | None:
    """Retourne un utilisateur par identifiant externe."""
    return db.scalar(select(User).where(User.external_id == external_id))


def list_users(db: Session) -> list[User]:
    """Retourne tous les utilisateurs."""
    return list(db.scalars(select(User).order_by(User.id)))
