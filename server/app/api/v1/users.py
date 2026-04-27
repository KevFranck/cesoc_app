"""Routes utilitaires MVP."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.app.api.deps import get_db
from server.app.schemas import UserRead, WorkstationRead
from server.app.repositories.user_repository import list_users
from server.app.repositories.workstation_repository import list_workstations


router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/users", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)) -> list[UserRead]:
    """Liste les utilisateurs disponibles."""
    return list_users(db)


@router.get("/workstations", response_model=list[WorkstationRead])
def get_workstations(db: Session = Depends(get_db)) -> list[WorkstationRead]:
    """Liste les postes disponibles."""
    return list_workstations(db)
