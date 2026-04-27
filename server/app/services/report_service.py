"""Service de reporting journalier."""

from datetime import date

from sqlalchemy.orm import Session

from server.app.core.time import get_local_today
from server.app.repositories import print_repository, session_repository


def build_daily_report(db: Session, target_date: date | None = None) -> dict[str, int | str]:
    """Construit les indicateurs journaliers."""
    report_date = target_date or get_local_today()

    return {
        "date": report_date.isoformat(),
        "total_connections": session_repository.count_started_on(db, report_date),
        "active_sessions": session_repository.count_active_started_on(db, report_date),
        "total_minutes_used": session_repository.total_minutes_on(db, report_date),
        "total_print_jobs": print_repository.count_jobs_on(db, report_date),
        "total_pages_printed": print_repository.total_pages_on(db, report_date),
        "blocked_print_jobs": print_repository.blocked_jobs_on(db, report_date),
    }
