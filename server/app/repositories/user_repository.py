"""Acces aux utilisateurs."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from server.app.models import User


def get_by_email(db: Session, email: str) -> User | None:
    """Retourne un utilisateur par email."""
    return db.scalar(select(User).where(User.email == email.lower().strip()))


def list_users(db: Session) -> list[User]:
    """Retourne tous les utilisateurs."""
    return list(db.scalars(select(User).order_by(User.id)))


def create_user(
    db: Session,
    *,
    email: str,
    first_name: str,
    last_name: str,
    password_hash: str,
    role: str = "user",
) -> User:
    """Cree un utilisateur applicatif."""
    user = User(
        email=email.lower().strip(),
        first_name=first_name,
        last_name=last_name,
        password_hash=password_hash,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
