"""Routes admin."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from server.app.api.deps import get_db
from server.app.schemas import AdminOverviewResponse
from server.app.services.admin_service import get_admin_overview


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=AdminOverviewResponse)
def admin_overview(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> AdminOverviewResponse:
    """Retourne les donnees du tableau de bord admin."""
    return AdminOverviewResponse(**get_admin_overview(db, limit=limit))
