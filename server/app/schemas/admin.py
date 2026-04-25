"""Schemas admin."""

from pydantic import BaseModel

from server.app.schemas.report import DailyReportResponse
from server.app.schemas.session import SessionResponse
from server.app.schemas.user import UserRead
from server.app.schemas.workstation import WorkstationRead


class PrintJobRead(BaseModel):
    """Representation d'une impression pour l'admin."""

    id: int
    pages: int
    status: str
    blocked_reason: str | None
    printed_at: str
    user: UserRead
    workstation: WorkstationRead


class AdminOverviewResponse(BaseModel):
    """Synthese admin pour le dashboard."""

    report: DailyReportResponse
    active_sessions: list[SessionResponse]
    recent_sessions: list[SessionResponse]
    recent_print_jobs: list[PrintJobRead]
