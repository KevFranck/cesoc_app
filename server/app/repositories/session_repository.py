"""Acces aux sessions."""

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from server.app.models import UserSession


def get_active_by_user(db: Session, user_id: int) -> UserSession | None:
    """Retourne la session active d'un utilisateur."""
    return db.scalar(
        select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.status == "active",
        )
    )


def get_by_id(db: Session, session_id: int) -> UserSession | None:
    """Retourne une session par son id."""
    return db.get(UserSession, session_id)


def list_active(db: Session) -> list[UserSession]:
    """Retourne les sessions actives."""
    stmt = (
        select(UserSession)
        .options(joinedload(UserSession.user), joinedload(UserSession.workstation))
        .where(UserSession.status == "active")
        .order_by(UserSession.started_at)
    )
    return list(db.scalars(stmt).unique())


def list_recent(db: Session, limit: int = 10) -> list[UserSession]:
    """Retourne les sessions les plus recentes avec relations."""
    stmt = (
        select(UserSession)
        .options(joinedload(UserSession.user), joinedload(UserSession.workstation))
        .order_by(UserSession.started_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).unique())


def count_started_on(db: Session, target_date: date) -> int:
    """Compte les sessions demarrees le jour donne."""
    return int(
        db.scalar(
            select(func.count(UserSession.id)).where(
                func.date(UserSession.started_at) == target_date
            )
        )
        or 0
    )


def total_minutes_on(db: Session, target_date: date) -> int:
    """Somme des minutes consommees pour le jour."""
    completed_minutes = int(
        db.scalar(
            select(func.coalesce(func.sum(UserSession.duration_minutes), 0)).where(
                func.date(UserSession.started_at) == target_date
            )
        )
        or 0
    )

    active_sessions = list(
        db.scalars(
            select(UserSession).where(
                UserSession.status == "active",
                func.date(UserSession.started_at) == target_date,
            )
        )
    )
    active_minutes = sum(int((datetime.utcnow() - session.started_at).total_seconds() // 60) for session in active_sessions)
    return completed_minutes + active_minutes
