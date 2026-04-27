"""Logique metier des sessions."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from server.app.core.time import get_utc_now_naive
from server.app.models import UserSession
from server.app.repositories import session_repository


def open_session(db: Session, user_id: int, workstation_id: int) -> UserSession:
    """Ouvre une session active."""
    user_session = UserSession(user_id=user_id, workstation_id=workstation_id, status="active")
    db.add(user_session)
    db.commit()
    db.refresh(user_session)
    return get_session_details(db, user_session.id)


def close_session(db: Session, session_id: int) -> UserSession:
    """Ferme une session active."""
    user_session = session_repository.get_by_id(db, session_id)
    if not user_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session introuvable.")

    if user_session.status != "active":
        return get_session_details(db, user_session.id)

    ended_at = get_utc_now_naive()
    duration_minutes = max(1, int((ended_at - user_session.started_at).total_seconds() // 60))

    user_session.ended_at = ended_at
    user_session.duration_minutes = duration_minutes
    user_session.status = "closed"
    db.add(user_session)
    db.commit()
    return get_session_details(db, user_session.id)


def list_active_sessions(db: Session) -> list[UserSession]:
    """Retourne la liste des sessions actives avec relations."""
    sessions = session_repository.list_active(db)
    return [get_session_details(db, session.id) for session in sessions]


def get_session_details(db: Session, session_id: int) -> UserSession:
    """Recharge une session avec les relations user et workstation."""
    query = (
        db.query(UserSession)
        .options(joinedload(UserSession.user), joinedload(UserSession.workstation))
        .filter(UserSession.id == session_id)
    )
    session_obj = query.one()
    return session_obj
