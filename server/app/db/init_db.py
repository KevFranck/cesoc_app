"""Initialisation de la base et des donnees de demonstration."""

from sqlalchemy import select

from server.app.db.base import Base
from server.app.db.session import SessionLocal, engine
from server.app.models import PrintJob, User, UserSession, Workstation


def init_db() -> None:
    """Cree les tables puis injecte quelques donnees de demo."""
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        existing_user = db.scalar(select(User).limit(1))
        if existing_user:
            return

        users = [
            User(external_id="CLI-001", first_name="Amina", last_name="Diallo", role="user", is_active=True),
            User(external_id="CLI-002", first_name="Jean", last_name="Tremblay", role="user", is_active=True),
            User(external_id="ADM-001", first_name="Sophie", last_name="Martin", role="admin", is_active=True),
        ]
        workstations = [
            Workstation(name="POSTE-01", location="Accueil", is_active=True),
            Workstation(name="POSTE-02", location="Accueil", is_active=True),
            Workstation(name="POSTE-03", location="Accueil", is_active=True),
        ]
        db.add_all(users + workstations)
        db.commit()

        # Force l'import dans les metadonnees et evite les warnings d'import inutilise.
        _ = PrintJob, UserSession
