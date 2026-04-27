"""Services admin."""

from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.app.core.security import hash_password
from server.app.core.time import get_local_today
from server.app.models import User
from server.app.repositories import (
    print_credit_repository,
    print_repository,
    session_repository,
    user_repository,
    workstation_repository,
)
from server.app.services.print_service import get_print_quota_status
from server.app.services.report_service import build_daily_report


def get_admin_overview(db: Session, limit: int = 10) -> dict[str, object]:
    """Construit l'overview admin."""
    return {
        "report": build_daily_report(db),
        "active_sessions": session_repository.list_active(db),
        "recent_sessions": session_repository.list_recent(db, limit=limit),
        "recent_print_jobs": [
            {
                "id": job.id,
                "pages": job.pages,
                "status": job.status,
                "blocked_reason": job.blocked_reason,
                "printed_at": job.printed_at.isoformat(),
                "user": job.user,
                "workstation": job.workstation,
            }
            for job in print_repository.list_recent(db, limit=limit)
        ],
    }


def list_admin_clients(db: Session) -> list[dict[str, object]]:
    """Retourne la liste des clients avec quelques statistiques utiles."""
    clients = []
    for user in user_repository.list_users(db):
        latest_session = session_repository.latest_for_user(db, user.id)
        bonus_pages_today = print_credit_repository.total_pages_for_user_on(db, user.id, get_local_today())
        clients.append(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "total_sessions": session_repository.count_for_user(db, user.id),
                "total_pages_printed": print_repository.total_pages_for_user(db, user.id),
                "total_print_jobs": print_repository.total_jobs_for_user(db, user.id),
                "bonus_pages_today": bonus_pages_today,
                "has_active_session": session_repository.get_active_by_user(db, user.id) is not None,
                "last_session_started_at": latest_session.started_at if latest_session else None,
                "last_workstation_name": latest_session.workstation.name if latest_session and latest_session.workstation else None,
            }
        )
    return clients


def reset_user_password(db: Session, user_id: int, new_password: str = "cesoc") -> User:
    """Reinitialise le mot de passe d'un utilisateur."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")

    user.password_hash = hash_password(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def build_recent_daily_reports(db: Session, days: int = 7) -> list[dict[str, int | str]]:
    """Construit une petite serie de rapports journaliers."""
    today = get_local_today()
    reports: list[dict[str, int | str]] = []
    for offset in range(days - 1, -1, -1):
        reports.append(build_daily_report(db, target_date=today - timedelta(days=offset)))
    return reports


def list_admin_workstations(db: Session):
    """Retourne la liste des postes."""
    return workstation_repository.list_workstations(db)


def create_admin_workstation(db: Session, *, name: str, location: str, is_active: bool):
    """Cree un poste si le nom n'existe pas deja."""
    if workstation_repository.get_by_name(db, name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Un poste avec ce nom existe deja.")
    return workstation_repository.create_workstation(db, name=name.strip(), location=location.strip(), is_active=is_active)


def update_admin_workstation(
    db: Session,
    workstation_id: int,
    *,
    name: str | None = None,
    location: str | None = None,
    is_active: bool | None = None,
):
    """Met a jour un poste."""
    workstation = workstation_repository.get_by_id(db, workstation_id)
    if not workstation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poste introuvable.")

    if name and name.strip() != workstation.name:
        existing = workstation_repository.get_by_name(db, name.strip())
        if existing and existing.id != workstation.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Un poste avec ce nom existe deja.")
        workstation.name = name.strip()
    if location is not None and location.strip():
        workstation.location = location.strip()
    if is_active is not None:
        workstation.is_active = is_active
    return workstation_repository.save(db, workstation)


def grant_manual_pages(db: Session, *, user_id: int, pages: int, reason: str | None = None) -> tuple[int, int]:
    """Ajoute des pages supplementaires pour aujourd'hui."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
    if pages <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le nombre de pages doit etre superieur a zero.")

    today = get_local_today()
    print_credit_repository.create_credit(
        db,
        user_id=user.id,
        pages=pages,
        reason=(reason or "Ajustement manuel admin").strip(),
        granted_for=today,
    )
    total_quota_today, _used_pages, remaining_quota = get_print_quota_status(db, user.email)
    return total_quota_today, remaining_quota
