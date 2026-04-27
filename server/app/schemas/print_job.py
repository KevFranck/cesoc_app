"""Schemas impression."""

from pydantic import BaseModel, Field


class PrintRequest(BaseModel):
    """Payload d'une demande d'impression."""

    email: str = Field(min_length=5, max_length=255)
    workstation_name: str = Field(min_length=3, max_length=50)
    pages: int = Field(ge=1, le=50)


class ObservedPrintRequest(BaseModel):
    """Payload d'un job d'impression detecte sur Windows."""

    email: str = Field(min_length=5, max_length=255)
    workstation_name: str = Field(min_length=3, max_length=50)
    pages: int = Field(ge=1, le=500)
    printer_name: str | None = Field(default=None, max_length=255)
    document_name: str | None = Field(default=None, max_length=255)
    spool_job_id: int | None = Field(default=None, ge=0)
    total_pages_seen: int | None = Field(default=None, ge=1, le=500)


class PrintResponse(BaseModel):
    """Reponse a une demande d'impression."""

    allowed: bool
    pages_requested: int
    pages_used_today: int
    remaining_quota: int
    message: str


class PrintQuotaResponse(BaseModel):
    """Etat du quota d'impression pour un utilisateur."""

    email: str
    daily_quota: int
    pages_used_today: int
    remaining_quota: int
