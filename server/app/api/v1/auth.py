"""Routes d'authentification."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.app.api.deps import get_db
from server.app.schemas import (
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    RegisterRequest,
    RegisterResponse,
)
from server.app.services.auth_service import change_user_password, login_user, register_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Connecte un utilisateur et ouvre sa session."""
    user, user_session = login_user(db, payload.email, payload.password, payload.workstation_name)
    return LoginResponse(
        message="Connexion reussie.",
        user=user,
        session=user_session,
    )


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    """Inscrit un nouveau client."""
    user = register_user(
        db,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password=payload.password,
    )
    return RegisterResponse(message="Inscription reussie.", user=user)


@router.post("/change-password", response_model=PasswordChangeResponse)
def change_password(payload: PasswordChangeRequest, db: Session = Depends(get_db)) -> PasswordChangeResponse:
    """Permet a un utilisateur de changer son mot de passe."""
    change_user_password(db, payload.email, payload.current_password, payload.new_password)
    return PasswordChangeResponse(message="Mot de passe modifie avec succes.")
