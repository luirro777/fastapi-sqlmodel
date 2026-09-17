from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from ..dependencies import SessionDep, get_current_user
from ..models import Hero, HeroCreate, HeroPublic, HeroUpdate

router = APIRouter(prefix="/heroes", tags=["heroes"])


# ---------------------------------------------------------------------------
# Endpoints públicos (lectura)
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    return session.exec(select(Hero).offset(offset).limit(limit)).all()


@router.get("/{hero_id}", response_model=HeroPublic)
def read_hero(
    hero_id: int,
    session: SessionDep,
):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found",
        )
    return hero


# ---------------------------------------------------------------------------
# Endpoints protegidos (escritura)
# `dependencies=[...]` corre get_current_user antes del handler.
# Si el token falta o es inválido -> 401 y el handler nunca se ejecuta.
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=HeroPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_hero(
    hero: HeroCreate,
    session: SessionDep,
):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.patch(
    "/{hero_id}",
    response_model=HeroPublic,
    dependencies=[Depends(get_current_user)],
)
def update_hero(
    hero_id: int,
    hero: HeroUpdate,
    session: SessionDep,
):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:  # antes decía `if not hero` -> nunca se disparaba
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found",
        )
    hero_data = hero.model_dump(exclude_unset=True)
    db_hero.sqlmodel_update(hero_data)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.delete(
    "/{hero_id}",
    dependencies=[Depends(get_current_user)],
)
def delete_hero(
    hero_id: int,
    session: SessionDep,
):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found",
        )
    session.delete(hero)
    session.commit()
    return {"ok": True}