"""Initialisation de la base."""

from sqlalchemy import delete, inspect, select, text
from sqlalchemy.orm import Session

from server.app.db.base import Base
from server.app.db.session import SessionLocal, engine
from server.app.models import PrintJob, User, UserSession, Workstation


def init_db() -> None:
    """Cree les tables puis initialise les postes par defaut."""
    Base.metadata.create_all(bind=engine)
    _ensure_user_schema_compatibility()
    _ensure_print_job_schema_compatibility()

    with SessionLocal() as db:
        _remove_demo_users(db)
        existing_workstation = db.scalar(select(Workstation).limit(1))
        if existing_workstation:
            return

        workstations = [
            Workstation(name="POSTE-01", location="Accueil", is_active=True),
            Workstation(name="POSTE-02", location="Accueil", is_active=True),
            Workstation(name="POSTE-03", location="Accueil", is_active=True),
        ]
        db.add_all(workstations)
        db.commit()

        # Force l'import dans les metadonnees et evite les warnings d'import inutilise.
        _ = PrintJob, UserSession


def _ensure_user_schema_compatibility() -> None:
    """Met a niveau une base locale ancienne vers le schema email/password_hash."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    statements: list[str] = []

    if "external_id" in columns and "email" not in columns:
        statements.append("ALTER TABLE users RENAME COLUMN external_id TO email")
        columns.remove("external_id")
        columns.add("email")

    if "password_hash" not in columns:
        statements.append("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
        statements.append("UPDATE users SET password_hash = '' WHERE password_hash IS NULL")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _remove_demo_users(db: Session) -> None:
    """Supprime les utilisateurs de demonstration historiques s'ils existent encore."""
    email_field = getattr(User, "email", None)
    if email_field is None:
        return

    legacy_demo_values = ("CLI-001", "CLI-002", "ADM-001")
    user_ids = list(
        db.scalars(
            select(User.id).where(email_field.in_(legacy_demo_values))
        )
    )
    if not user_ids:
        return

    db.execute(delete(PrintJob).where(PrintJob.user_id.in_(user_ids)))
    db.execute(delete(UserSession).where(UserSession.user_id.in_(user_ids)))
    db.execute(delete(User).where(User.id.in_(user_ids)))
    db.commit()


def _ensure_print_job_schema_compatibility() -> None:
    """Met a niveau la table print_jobs pour le suivi robuste des jobs spooler."""
    inspector = inspect(engine)
    if "print_jobs" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("print_jobs")}
    statements: list[str] = []

    if "printer_name" not in columns:
        statements.append("ALTER TABLE print_jobs ADD COLUMN printer_name VARCHAR(255)")
    if "document_name" not in columns:
        statements.append("ALTER TABLE print_jobs ADD COLUMN document_name VARCHAR(255)")
    if "spool_job_id" not in columns:
        statements.append("ALTER TABLE print_jobs ADD COLUMN spool_job_id INTEGER")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
