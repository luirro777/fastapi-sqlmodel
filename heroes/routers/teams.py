from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

# Importamos la dependencia del usuario actual junto con la de sesión
from ..dependencies import CurrentUserDep, SessionDep
from ..models import Team, TeamCreate, TeamPublic, TeamUpdate

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/", response_model=TeamPublic)
def create_team(
    team: TeamCreate,
    session: SessionDep,
    usuario_actual: CurrentUserDep  # 🔒 Ruta protegida
):
    db_team = Team.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team

@router.get("/", response_model=list[TeamPublic])
def read_items(
    session: SessionDep,
    usuario_actual: CurrentUserDep,  # 🔒 Ruta protegida
    offset: int = 0,
    limit: int = Query(default=100, le=100)
):
    return session.exec(select(Team).offset(offset).limit(limit)).all()

@router.get("/{team_id}", response_model=TeamPublic)
def read_team(
    team_id: int,
    session: SessionDep,
    usuario_actual: CurrentUserDep  # 🔒 Ruta protegida
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.patch("/{team_id}", response_model=TeamPublic)
def update_team(
    team_id: int,
    team: TeamUpdate,
    session: SessionDep,
    usuario_actual: CurrentUserDep  # 🔒 Ruta protegida
):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team

@router.delete("/{team_id}")
def delete_team(
    team_id: int,
    session: SessionDep,
    usuario_actual: CurrentUserDep  # 🔒 Ruta protegida
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {
        "ok": True
    }
