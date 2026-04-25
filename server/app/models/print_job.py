"""Modele d'impression."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.db.base import Base


class PrintJob(Base):
    """Trace une demande d'impression."""

    __tablename__ = "print_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    workstation_id: Mapped[int] = mapped_column(ForeignKey("workstations.id"), index=True)
    pages: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="allowed")
    blocked_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    printed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="print_jobs")
    workstation = relationship("Workstation", back_populates="print_jobs")
