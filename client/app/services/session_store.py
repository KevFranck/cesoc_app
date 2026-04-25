"""Etat courant du client desktop."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class CurrentSession:
    """Session locale du poste."""

    session_id: int
    external_id: str
    user_name: str
    workstation_name: str
    started_at: datetime
    workspace_path: Path
