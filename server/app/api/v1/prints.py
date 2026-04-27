"""Routes d'impression."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from server.app.api.deps import get_db
from server.app.schemas import ObservedPrintRequest, PrintQuotaResponse, PrintRequest, PrintResponse
from server.app.services.print_service import get_print_quota_status, register_observed_print, register_print


router = APIRouter(prefix="/prints", tags=["prints"])


@router.get("/quota", response_model=PrintQuotaResponse)
def get_print_quota(
    email: str = Query(..., min_length=5, max_length=255),
    db: Session = Depends(get_db),
) -> PrintQuotaResponse:
    """Retourne le quota journalier restant pour un utilisateur."""
    daily_quota, pages_used_today, remaining_quota = get_print_quota_status(db, email)
    return PrintQuotaResponse(
        email=email,
        daily_quota=daily_quota,
        pages_used_today=pages_used_today,
        remaining_quota=remaining_quota,
    )


@router.post("", response_model=PrintResponse)
def create_print_job(payload: PrintRequest, db: Session = Depends(get_db)) -> PrintResponse:
    """Valide ou bloque une impression selon le quota."""
    allowed, pages_used_today, remaining_quota = register_print(
        db,
        payload.email,
        payload.workstation_name,
        payload.pages,
    )
    message = "Impression autorisee." if allowed else "Impression bloquee : quota quotidien de 10 pages atteint."
    return PrintResponse(
        allowed=allowed,
        pages_requested=payload.pages,
        pages_used_today=pages_used_today,
        remaining_quota=remaining_quota,
        message=message,
    )


@router.post("/observe", response_model=PrintResponse)
def observe_print_job(payload: ObservedPrintRequest, db: Session = Depends(get_db)) -> PrintResponse:
    """Journalise un job observe sur Windows et indique s'il doit etre bloque."""
    allowed, pages_used_today, remaining_quota = register_observed_print(
        db,
        payload.email,
        payload.workstation_name,
        payload.pages,
        printer_name=payload.printer_name,
        document_name=payload.document_name,
        spool_job_id=payload.spool_job_id,
        total_pages_seen=payload.total_pages_seen,
    )
    message = (
        "Impression detectee et autorisee."
        if allowed
        else "Impression detectee mais bloquee : quota quotidien de 10 pages atteint."
    )
    return PrintResponse(
        allowed=allowed,
        pages_requested=payload.pages,
        pages_used_today=pages_used_today,
        remaining_quota=remaining_quota,
        message=message,
    )
