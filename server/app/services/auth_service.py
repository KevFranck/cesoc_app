"""Logique d'authentification utilisateur."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from server.app.core.security import hash_password, verify_password
from server.app.repositories import session_repository, user_repository, workstation_repository
from server.app.services.session_service import get_session_details, open_session


def register_user(
    db: Session,
    *,
    email: str,
    first_name: str,
    last_name: str,
    password: str,
):
    """Inscrit un client applicatif avec mot de passe."""
    existing_user = user_repository.get_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse email existe deja.",
        )

    return user_repository.create_user(
        db,
        email=email,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        password_hash=hash_password(password),
        role="user",
    )


def login_user(db: Session, email: str, password: str, workstation_name: str):
    """Valide l'utilisateur et ouvre une session applicative."""
    user = user_repository.get_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable ou inactif.")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mot de passe invalide.")

    workstation = workstation_repository.get_by_name(db, workstation_name)
    if not workstation or not workstation.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poste introuvable ou inactif.")

    active_session = session_repository.get_active_by_user(db, user.id)
    if active_session:
        return user, get_session_details(db, active_session.id)

    created_session = open_session(db, user.id, workstation.id)
    return user, created_session


def change_user_password(db: Session, email: str, current_password: str, new_password: str) -> None:
    """Permet a un utilisateur connecte de modifier son mot de passe."""
    user = user_repository.get_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable ou inactif.")
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mot de passe actuel invalide.")
    if current_password == new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le nouveau mot de passe doit etre different.")

    user.password_hash = hash_password(new_password)
    db.add(user)
    db.commit()
