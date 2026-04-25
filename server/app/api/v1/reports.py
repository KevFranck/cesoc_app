"""Routes de reporting."""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.app.api.deps import get_db
from server.app.schemas import DailyReportResponse
from server.app.services.report_service import build_daily_report


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/daily", response_model=DailyReportResponse)
def daily_report(target_date: date | None = None, db: Session = Depends(get_db)) -> DailyReportResponse:
    """Retourne les indicateurs de la journee."""
    return DailyReportResponse(**build_daily_report(db, target_date=target_date))
