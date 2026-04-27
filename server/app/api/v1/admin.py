"""Routes admin."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from server.app.api.deps import get_db
from server.app.schemas import (
    AdminClientRead,
    AdminOverviewResponse,
    DailyReportResponse,
    PasswordResetResponse,
    PrintCreditGrantRequest,
    PrintCreditGrantResponse,
    WorkstationCreateRequest,
    WorkstationRead,
    WorkstationUpdateRequest,
)
from server.app.services.admin_service import (
    build_recent_daily_reports,
    create_admin_workstation,
    grant_manual_pages,
    get_admin_overview,
    list_admin_clients,
    list_admin_workstations,
    reset_user_password,
    update_admin_workstation,
)


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=AdminOverviewResponse)
def admin_overview(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> AdminOverviewResponse:
    """Retourne les donnees du tableau de bord admin."""
    return AdminOverviewResponse(**get_admin_overview(db, limit=limit))


@router.get("/clients", response_model=list[AdminClientRead])
def admin_clients(db: Session = Depends(get_db)) -> list[AdminClientRead]:
    """Retourne la liste des clients."""
    return [AdminClientRead(**client) for client in list_admin_clients(db)]


@router.post("/clients/{user_id}/grant-pages", response_model=PrintCreditGrantResponse)
def admin_grant_pages(
    user_id: int,
    payload: PrintCreditGrantRequest,
    db: Session = Depends(get_db),
) -> PrintCreditGrantResponse:
    """Ajoute des pages supplementaires a un utilisateur pour aujourd'hui."""
    total_quota_today, remaining_quota = grant_manual_pages(
        db,
        user_id=user_id,
        pages=payload.pages,
        reason=payload.reason,
    )
    return PrintCreditGrantResponse(
        message=f"{payload.pages} page(s) ajoutee(s) pour aujourd'hui.",
        granted_pages=payload.pages,
        total_quota_today=total_quota_today,
        remaining_quota=remaining_quota,
    )


@router.post("/clients/{user_id}/reset-password", response_model=PasswordResetResponse)
def admin_reset_password(user_id: int, db: Session = Depends(get_db)) -> PasswordResetResponse:
    """Reinitialise le mot de passe d'un client a `cesoc`."""
    user = reset_user_password(db, user_id, new_password="cesoc")
    return PasswordResetResponse(
        message="Mot de passe reinitialise a 'cesoc'.",
        user=user,
    )


@router.get("/reports/daily", response_model=list[DailyReportResponse])
def admin_daily_reports(
    days: int = Query(default=7, ge=1, le=31),
    db: Session = Depends(get_db),
) -> list[DailyReportResponse]:
    """Retourne une serie recente de rapports journaliers."""
    return [DailyReportResponse(**report) for report in build_recent_daily_reports(db, days=days)]


@router.get("/workstations", response_model=list[WorkstationRead])
def admin_workstations(db: Session = Depends(get_db)) -> list[WorkstationRead]:
    """Retourne la liste des postes."""
    return list_admin_workstations(db)


@router.post("/workstations", response_model=WorkstationRead, status_code=201)
def admin_create_workstation(payload: WorkstationCreateRequest, db: Session = Depends(get_db)) -> WorkstationRead:
    """Cree un nouveau poste."""
    return create_admin_workstation(db, name=payload.name, location=payload.location, is_active=payload.is_active)


@router.patch("/workstations/{workstation_id}", response_model=WorkstationRead)
def admin_update_workstation(
    workstation_id: int,
    payload: WorkstationUpdateRequest,
    db: Session = Depends(get_db),
) -> WorkstationRead:
    """Met a jour un poste."""
    return update_admin_workstation(
        db,
        workstation_id,
        name=payload.name,
        location=payload.location,
        is_active=payload.is_active,
    )
