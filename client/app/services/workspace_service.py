"""Gestion d'un espace de travail local par session."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


class WorkspaceService:
    """Cree un dossier local pour la session courante."""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = (
            Path(workspace_root)
            if workspace_root.strip()
            else Path.home() / "Documents" / "CESOC Sessions"
        )

    def ensure_session_workspace(
        self,
        email: str,
        workstation_name: str,
        started_at: datetime,
    ) -> Path:
        """Cree le dossier de travail de la session si besoin."""
        safe_timestamp = started_at.strftime("%Y%m%d-%H%M%S")
        safe_email = email.replace("@", "_at_").replace(".", "_")
        session_dir = self.workspace_root / safe_email / f"{workstation_name}-{safe_timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)

        readme = session_dir / "LISEZ-MOI.txt"
        if not readme.exists():
            readme.write_text(
                "\n".join(
                    [
                        "Dossier de travail CESOC",
                        "",
                        "Vous pouvez utiliser ce dossier pendant les tests.",
                        "Placez ici les documents de la session en cours.",
                    ]
                ),
                encoding="utf-8",
            )

        return session_dir
