"""Services admin."""

from sqlalchemy.orm import Session

from server.app.repositories import print_repository, session_repository
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
