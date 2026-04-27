"""Schemas admin."""

from datetime import datetime

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


class AdminClientRead(BaseModel):
    """Representation enrichie d'un client pour l'admin."""

    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    total_sessions: int
    total_pages_printed: int
    total_print_jobs: int
    bonus_pages_today: int
    has_active_session: bool
    last_session_started_at: datetime | None
    last_workstation_name: str | None


class PasswordResetResponse(BaseModel):
    """Reponse de reinitialisation de mot de passe."""

    message: str
    user: UserRead


class PrintCreditGrantRequest(BaseModel):
    """Demande d'ajout manuel de pages."""

    pages: int
    reason: str | None = None


class PrintCreditGrantResponse(BaseModel):
    """Reponse d'ajout manuel de pages."""

    message: str
    granted_pages: int
    total_quota_today: int
    remaining_quota: int


class WorkstationCreateRequest(BaseModel):
    """Creation d'un poste."""

    name: str
    location: str
    is_active: bool = True


class WorkstationUpdateRequest(BaseModel):
    """Mise a jour d'un poste."""

    name: str | None = None
    location: str | None = None
    is_active: bool | None = None
