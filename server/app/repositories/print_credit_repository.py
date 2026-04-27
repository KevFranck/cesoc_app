"""Acces aux credits d'impression manuels."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from server.app.models import PrintCredit


def total_pages_for_user_on(db: Session, user_id: int, target_date: date) -> int:
    """Retourne le total de pages accorde pour un utilisateur un jour donne."""
    return int(
        db.scalar(
            select(func.coalesce(func.sum(PrintCredit.pages), 0)).where(
                PrintCredit.user_id == user_id,
                PrintCredit.granted_for == target_date,
            )
        )
        or 0
    )


def create_credit(
    db: Session,
    *,
    user_id: int,
    pages: int,
    reason: str,
    granted_for: date,
) -> PrintCredit:
    """Cree un credit manuel."""
    credit = PrintCredit(
        user_id=user_id,
        pages=pages,
        reason=reason,
        granted_for=granted_for,
    )
    db.add(credit)
    db.commit()
    db.refresh(credit)
    return credit
