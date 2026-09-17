from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from ..dependencies import SessionDep, get_current_user
from ..models import Team, TeamCreate, TeamPublic, TeamUpdate

router = APIRouter(prefix="/teams", tags=["teams"])


# ---------------------------------------------------------------------------
# Endpoints públicos (lectura)
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[TeamPublic])
def read_teams(  # antes se llamaba read_items
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    return session.exec(select(Team).offset(offset).limit(limit)).all()


@router.get("/{team_id}", response_model=TeamPublic)
def read_team(
    team_id: int,
    session: SessionDep,
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    return team


# ---------------------------------------------------------------------------
# Endpoints protegidos (escritura)
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=TeamPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_team(
    team: TeamCreate,
    session: SessionDep,
):
    db_team = Team.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@router.patch(
    "/{team_id}",
    response_model=TeamPublic,
    dependencies=[Depends(get_current_user)],
)
def update_team(
    team_id: int,
    team: TeamUpdate,
    session: SessionDep,
):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@router.delete(
    "/{team_id}",
    dependencies=[Depends(get_current_user)],
)
def delete_team(
    team_id: int,
    session: SessionDep,
):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    session.delete(team)
    session.commit()
    return {"ok": True}