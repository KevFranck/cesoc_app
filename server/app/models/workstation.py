"""Modele poste informatique."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.db.base import Base


class Workstation(Base):
    """Poste informatique configure dans le systeme."""

    __tablename__ = "workstations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    location: Mapped[str] = mapped_column(String(100), default="Accueil")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sessions = relationship("UserSession", back_populates="workstation")
    print_jobs = relationship("PrintJob", back_populates="workstation")
