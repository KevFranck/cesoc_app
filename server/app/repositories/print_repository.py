"""Acces aux impressions."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from server.app.core.time import get_local_day_bounds
from server.app.models import PrintJob


def pages_used_on(db: Session, user_id: int, target_date: date) -> int:
    """Retourne le nombre de pages autorisees utilisees par jour."""
    start_local, end_local = get_local_day_bounds(target_date)
    return int(
        db.scalar(
            select(func.coalesce(func.sum(PrintJob.pages), 0)).where(
                PrintJob.user_id == user_id,
                PrintJob.status == "allowed",
                PrintJob.printed_at >= start_local,
                PrintJob.printed_at < end_local,
            )
        )
        or 0
    )


def allowed_jobs_used_on(db: Session, user_id: int, target_date: date) -> int:
    """Retourne le nombre d'impressions autorisees utilisees par jour."""
    start_local, end_local = get_local_day_bounds(target_date)
    return int(
        db.scalar(
            select(func.count(PrintJob.id)).where(
                PrintJob.user_id == user_id,
                PrintJob.status == "allowed",
                PrintJob.printed_at >= start_local,
                PrintJob.printed_at < end_local,
            )
        )
        or 0
    )


def count_jobs_on(db: Session, target_date: date) -> int:
    """Compte le nombre d'impressions du jour."""
    start_local, end_local = get_local_day_bounds(target_date)
    return int(
        db.scalar(
            select(func.count(PrintJob.id)).where(
                PrintJob.printed_at >= start_local,
                PrintJob.printed_at < end_local,
            )
        )
        or 0
    )


def total_pages_on(db: Session, target_date: date) -> int:
    """Retourne le total de pages autorisees du jour."""
    start_local, end_local = get_local_day_bounds(target_date)
    return int(
        db.scalar(
            select(func.coalesce(func.sum(PrintJob.pages), 0)).where(
                PrintJob.status == "allowed",
                PrintJob.printed_at >= start_local,
                PrintJob.printed_at < end_local,
            )
        )
        or 0
    )


def blocked_jobs_on(db: Session, target_date: date) -> int:
    """Compte les impressions bloquees du jour."""
    start_local, end_local = get_local_day_bounds(target_date)
    return int(
        db.scalar(
            select(func.count(PrintJob.id)).where(
                PrintJob.status == "blocked",
                PrintJob.printed_at >= start_local,
                PrintJob.printed_at < end_local,
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


def get_observed_job_for_spool(
    db: Session,
    *,
    user_id: int,
    workstation_id: int,
    spool_job_id: int,
    target_date: date,
) -> PrintJob | None:
    """Retourne un job spooler deja observe pour l'utilisateur/poste/jour."""
    start_local, end_local = get_local_day_bounds(target_date)
    return db.scalar(
        select(PrintJob).where(
            PrintJob.user_id == user_id,
            PrintJob.workstation_id == workstation_id,
            PrintJob.spool_job_id == spool_job_id,
            PrintJob.printed_at >= start_local,
            PrintJob.printed_at < end_local,
        )
    )


def save(db: Session, print_job: PrintJob) -> PrintJob:
    """Persiste un job d'impression."""
    db.add(print_job)
    db.commit()
    db.refresh(print_job)
    return print_job


def total_pages_for_user(db: Session, user_id: int) -> int:
    """Retourne le total des pages autorisees pour un utilisateur."""
    return int(
        db.scalar(
            select(func.coalesce(func.sum(PrintJob.pages), 0)).where(
                PrintJob.user_id == user_id,
                PrintJob.status == "allowed",
            )
        )
        or 0
    )


def total_jobs_for_user(db: Session, user_id: int) -> int:
    """Retourne le total des travaux d'impression d'un utilisateur."""
    return int(
        db.scalar(select(func.count(PrintJob.id)).where(PrintJob.user_id == user_id)) or 0
    )
