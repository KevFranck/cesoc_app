"""Logique metier pour les impressions."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.app.core.config import get_settings
from server.app.core.time import get_local_today
from server.app.models import PrintJob
from server.app.repositories import (
    print_credit_repository,
    print_repository,
    user_repository,
    workstation_repository,
)


settings = get_settings()


def register_print(db: Session, email: str, workstation_name: str, pages: int) -> tuple[bool, int, int]:
    """Enregistre une impression, autorisee ou bloquee selon le quota."""
    user = user_repository.get_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable ou inactif.")

    workstation = workstation_repository.get_by_name(db, workstation_name)
    if not workstation or not workstation.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poste introuvable ou inactif.")

    today = get_local_today()
    used_pages = print_repository.pages_used_on(db, user.id, today)
    credited_pages = print_credit_repository.total_pages_for_user_on(db, user.id, today)
    remaining_quota = max(settings.default_daily_print_quota + credited_pages - used_pages, 0)
    allowed = pages <= remaining_quota

    print_job = PrintJob(
        user_id=user.id,
        workstation_id=workstation.id,
        pages=pages,
        status="allowed" if allowed else "blocked",
        blocked_reason=None if allowed else "Quota quotidien d'impression depasse.",
    )
    db.add(print_job)
    db.commit()

    new_used_pages = used_pages + pages if allowed else used_pages
    new_remaining = max(settings.default_daily_print_quota + credited_pages - new_used_pages, 0)
    return allowed, new_used_pages, new_remaining


def register_observed_print(
    db: Session,
    email: str,
    workstation_name: str,
    pages: int,
    printer_name: str | None = None,
    document_name: str | None = None,
    spool_job_id: int | None = None,
    total_pages_seen: int | None = None,
) -> tuple[bool, int, int]:
    """Enregistre un job detecte sur le spooler Windows."""
    user = user_repository.get_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable ou inactif.")

    workstation = workstation_repository.get_by_name(db, workstation_name)
    if not workstation or not workstation.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poste introuvable ou inactif.")

    today = get_local_today()
    normalized_total = max(1, int(total_pages_seen or pages))
    existing_job = None
    if spool_job_id is not None:
        existing_job = print_repository.get_observed_job_for_spool(
            db,
            user_id=user.id,
            workstation_id=workstation.id,
            spool_job_id=spool_job_id,
            target_date=today,
        )

    used_pages = print_repository.pages_used_on(db, user.id, today)
    credited_pages = print_credit_repository.total_pages_for_user_on(db, user.id, today)
    existing_allowed_pages = existing_job.pages if existing_job and existing_job.status == "allowed" else 0
    used_pages_excluding_current = max(used_pages - existing_allowed_pages, 0)
    total_quota = settings.default_daily_print_quota + credited_pages
    remaining_quota_before_current = max(total_quota - used_pages_excluding_current, 0)
    allowed = normalized_total <= remaining_quota_before_current

    if existing_job:
        existing_job.pages = normalized_total
        existing_job.status = "allowed" if allowed else "blocked"
        existing_job.blocked_reason = None if allowed else "Quota quotidien d'impression depasse."
        existing_job.printer_name = printer_name
        existing_job.document_name = document_name
        print_repository.save(db, existing_job)
    else:
        print_repository.save(
            db,
            PrintJob(
                user_id=user.id,
                workstation_id=workstation.id,
                pages=normalized_total,
                status="allowed" if allowed else "blocked",
                blocked_reason=None if allowed else "Quota quotidien d'impression depasse.",
                printer_name=printer_name,
                document_name=document_name,
                spool_job_id=spool_job_id,
            ),
        )

    new_used_pages = used_pages_excluding_current + (normalized_total if allowed else 0)
    new_remaining = max(total_quota - new_used_pages, 0)
    return allowed, new_used_pages, new_remaining


def get_print_quota_status(db: Session, email: str) -> tuple[int, int, int]:
    """Retourne l'etat du quota du jour pour un utilisateur."""
    user = user_repository.get_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable ou inactif.")

    today = get_local_today()
    used_pages = print_repository.pages_used_on(db, user.id, today)
    credited_pages = print_credit_repository.total_pages_for_user_on(db, user.id, today)
    total_quota = settings.default_daily_print_quota + credited_pages
    remaining_quota = max(total_quota - used_pages, 0)
    return total_quota, used_pages, remaining_quota
