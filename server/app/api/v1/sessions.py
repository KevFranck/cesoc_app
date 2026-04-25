"""Routes de sessions."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.app.api.deps import get_db
from server.app.schemas import SessionCloseResponse, SessionResponse
from server.app.services.session_service import close_session, list_active_sessions


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/active", response_model=list[SessionResponse])
def get_active_sessions(db: Session = Depends(get_db)) -> list[SessionResponse]:
    """Liste les sessions encore ouvertes."""
    return list_active_sessions(db)


@router.post("/{session_id}/close", response_model=SessionCloseResponse)
def close_user_session(session_id: int, db: Session = Depends(get_db)) -> SessionCloseResponse:
    """Ferme une session utilisateur."""
    closed_session = close_session(db, session_id)
    return SessionCloseResponse(session=closed_session, message="Session fermee.")
