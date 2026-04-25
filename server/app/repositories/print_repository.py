"""Acces aux impressions."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from server.app.models import PrintJob


def pages_used_on(db: Session, user_id: int, target_date: date) -> int:
    """Retourne le nombre de pages autorisees utilisees par jour."""
    return int(
        db.scalar(
            select(func.coalesce(func.sum(PrintJob.pages), 0)).where(
                PrintJob.user_id == user_id,
                PrintJob.status == "allowed",
                func.date(PrintJob.printed_at) == target_date,
            )
        )
        or 0
    )


def count_jobs_on(db: Session, target_date: date) -> int:
    """Compte le nombre d'impressions du jour."""
    return int(
        db.scalar(
            select(func.count(PrintJob.id)).where(
                func.date(PrintJob.printed_at) == target_date
            )
        )
        or 0
    )


def total_pages_on(db: Session, target_date: date) -> int:
    """Retourne le total de pages autorisees du jour."""
    return int(
        db.scalar(
            select(func.coalesce(func.sum(PrintJob.pages), 0)).where(
                PrintJob.status == "allowed",
                func.date(PrintJob.printed_at) == target_date,
            )
        )
        or 0
    )


def blocked_jobs_on(db: Session, target_date: date) -> int:
    """Compte les impressions bloquees du jour."""
    return int(
        db.scalar(
            select(func.count(PrintJob.id)).where(
                PrintJob.status == "blocked",
                func.date(PrintJob.printed_at) == target_date,
            )
        )
        or 0
    )


def list_recent(db: Session, limit: int = 10) -> list[PrintJob]:
    """Retourne les impressions les plus recentes avec relations."""
    stmt = (
        select(PrintJob)
        .options(joinedload(PrintJob.user), joinedload(PrintJob.workstation))
        .order_by(PrintJob.printed_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).unique())
