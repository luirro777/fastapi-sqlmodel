from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from ..dependencies import SessionDep
from ..models import Hero, HeroCreate, HeroPublic, HeroUpdate

router = APIRouter(prefix="/heroes", tags=["heroes"])

@router.post("/", response_model=HeroPublic)
async def create_hero(
    hero: HeroCreate,
    session: SessionDep
):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@router.get("/", response_model=list[HeroPublic])
async def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100)
):
    return session.exec(select(Hero).offset(offset).limit(limit)).all()

@router.get("/{hero_id}", response_model=HeroPublic)
async def read_hero(
    hero_id: int,
    session: SessionDep
):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@router.patch("/{hero_id}", response_model=HeroPublic)
async def update_hero(
    hero_id: int,
    hero: HeroUpdate,
    session: SessionDep
):
    db_hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    db_hero.sqlmodel_update(hero_data)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero

@router.delete("/{hero_id}")
async def delete_hero(
    hero_id: int,
    session: SessionDep
):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return{
        "ok": True
    }

