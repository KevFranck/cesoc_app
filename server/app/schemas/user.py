"""Schemas utilisateur."""

from datetime import datetime

from pydantic import BaseModel


class UserRead(BaseModel):
    """Representation publique d'un utilisateur."""

    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
