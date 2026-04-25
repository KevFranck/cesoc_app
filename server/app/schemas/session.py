"""Schemas session."""

from datetime import datetime

from pydantic import BaseModel

from server.app.schemas.user import UserRead
from server.app.schemas.workstation import WorkstationRead


class SessionResponse(BaseModel):
    """Session utilisateur retournee par l'API."""

    id: int
    status: str
    started_at: datetime
    ended_at: datetime | None
    duration_minutes: int
    user: UserRead
    workstation: WorkstationRead

    model_config = {"from_attributes": True}


class SessionCloseResponse(BaseModel):
    """Reponse lors de la fermeture d'une session."""

    session: SessionResponse
    message: str
