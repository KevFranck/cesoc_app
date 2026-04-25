"""Routes d'authentification."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.app.api.deps import get_db
from server.app.schemas import LoginRequest, LoginResponse
from server.app.services.auth_service import login_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Connecte un utilisateur et ouvre sa session."""
    user, user_session = login_user(db, payload.external_id, payload.workstation_name)
    return LoginResponse(
        message="Connexion reussie.",
        user=user,
        session=user_session,
    )
