"""Logique de connexion utilisateur."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.app.repositories import session_repository, user_repository, workstation_repository
from server.app.services.session_service import get_session_details, open_session


def login_user(db: Session, external_id: str, workstation_name: str):
    """Valide l'utilisateur et ouvre une session applicative."""
    user = user_repository.get_by_external_id(db, external_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable ou inactif.")

    workstation = workstation_repository.get_by_name(db, workstation_name)
    if not workstation or not workstation.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poste introuvable ou inactif.")

    active_session = session_repository.get_active_by_user(db, user.id)
    if active_session:
        return user, get_session_details(db, active_session.id)

    created_session = open_session(db, user.id, workstation.id)
    return user, created_session
