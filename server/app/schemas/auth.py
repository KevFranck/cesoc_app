"""Schemas d'authentification."""

from pydantic import BaseModel, Field

from server.app.schemas.session import SessionResponse
from server.app.schemas.user import UserRead


class LoginRequest(BaseModel):
    """Payload de connexion."""

    external_id: str = Field(min_length=3, max_length=50)
    workstation_name: str = Field(min_length=3, max_length=50)


class LoginResponse(BaseModel):
    """Reponse de connexion."""

    message: str
    user: UserRead
    session: SessionResponse
