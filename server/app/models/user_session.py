"""Modele de session utilisateur."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.time import get_utc_now_naive
from server.app.db.base import Base


class UserSession(Base):
    """Session d'utilisation d'un poste."""

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    workstation_id: Mapped[int] = mapped_column(ForeignKey("workstations.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now_naive)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)

    user = relationship("User", back_populates="sessions")
    workstation = relationship("Workstation", back_populates="sessions")
