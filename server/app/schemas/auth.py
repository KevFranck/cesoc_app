"""Schemas d'authentification."""

from pydantic import BaseModel, Field

from server.app.schemas.session import SessionResponse
from server.app.schemas.user import UserRead


class LoginRequest(BaseModel):
    """Payload de connexion."""

    email: str = Field(min_length=5, max_length=255)
    password: str = Field(max_length=128)
    workstation_name: str = Field(min_length=3, max_length=50)


class RegisterRequest(BaseModel):
    """Payload d'inscription client."""

    email: str = Field(min_length=5, max_length=255)
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    password: str = Field(max_length=128)


class RegisterResponse(BaseModel):
    """Reponse d'inscription."""

    message: str
    user: UserRead


class PasswordChangeRequest(BaseModel):
    """Demande de changement de mot de passe."""

    email: str = Field(min_length=5, max_length=255)
    current_password: str = Field(max_length=128)
    new_password: str = Field(max_length=128)


class PasswordChangeResponse(BaseModel):
    """Reponse de changement de mot de passe."""

    message: str


class LoginResponse(BaseModel):
    """Reponse de connexion."""

    message: str
    user: UserRead
    session: SessionResponse
