"""Schemas reporting."""

from pydantic import BaseModel


class DailyReportResponse(BaseModel):
    """Indicateurs journaliers."""

    date: str
    total_connections: int
    active_sessions: int
    total_minutes_used: int
    total_print_jobs: int
    total_pages_printed: int
    blocked_print_jobs: int
