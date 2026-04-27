"""Credits de pages accordes manuellement par un administrateur."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.time import get_local_now, get_local_today
from server.app.db.base import Base


class PrintCredit(Base):
    """Ajout manuel de pages pour un utilisateur sur une journee."""

    __tablename__ = "print_credits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    pages: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(255), default="Ajustement manuel admin")
    granted_for: Mapped[date] = mapped_column(Date, default=get_local_today, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_local_now)

    user = relationship("User", back_populates="print_credits")
