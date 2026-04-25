"""Schemas poste informatique."""

from datetime import datetime

from pydantic import BaseModel


class WorkstationRead(BaseModel):
    """Representation publique d'un poste."""

    id: int
    name: str
    location: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
