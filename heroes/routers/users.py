from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..dependencies import CurrentUser, SessionDep
from ..models import User, UserCreate, UserPublic
from ..security import hash_password

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: SessionDep):
    existing = session.exec(
        select(User).where(User.username == user.username)
    ).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "El usuario ya existe")

    db_user = User.model_validate(
        user, update={"hashed_password": hash_password(user.password)}
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserPublic)
def read_users_me(current_user: CurrentUser):
    return current_user