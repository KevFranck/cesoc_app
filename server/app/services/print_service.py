"""Logique metier pour les impressions."""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.app.core.config import get_settings
from server.app.models import PrintJob
from server.app.repositories import print_repository, user_repository, workstation_repository


settings = get_settings()


def register_print(db: Session, external_id: str, workstation_name: str, pages: int) -> tuple[bool, int, int]:
    """Enregistre une impression, autorisee ou bloquee selon le quota."""
    user = user_repository.get_by_external_id(db, external_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable ou inactif.")

    workstation = workstation_repository.get_by_name(db, workstation_name)
    if not workstation or not workstation.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poste introuvable ou inactif.")

    today = datetime.utcnow().date()
    used_pages = print_repository.pages_used_on(db, user.id, today)
    remaining_quota = max(settings.default_daily_print_quota - used_pages, 0)
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
    new_remaining = max(settings.default_daily_print_quota - new_used_pages, 0)
    return allowed, new_used_pages, new_remaining


def register_observed_print(
    db: Session,
    external_id: str,
    workstation_name: str,
    pages: int,
    printer_name: str | None = None,
    document_name: str | None = None,
    spool_job_id: int | None = None,
) -> tuple[bool, int, int]:
    """Enregistre un job detecte sur le spooler Windows."""
    _ = printer_name, document_name, spool_job_id
    normalized_pages = max(1, pages)
    return register_print(db, external_id, workstation_name, normalized_pages)


def get_print_quota_status(db: Session, external_id: str) -> tuple[int, int, int]:
    """Retourne l'etat du quota du jour pour un utilisateur."""
    user = user_repository.get_by_external_id(db, external_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable ou inactif.")

    today = datetime.utcnow().date()
    used_pages = print_repository.pages_used_on(db, user.id, today)
    remaining_quota = max(settings.default_daily_print_quota - used_pages, 0)
    return settings.default_daily_print_quota, used_pages, remaining_quota
