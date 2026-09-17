from sqlmodel import Field, Relationship, SQLModel
from pydantic import EmailStr

#################### TEAM ###########################
class TeamBase(SQLModel):
    name: str = Field(index=True)
    headquarters: str


class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True) 
    heroes: list["Hero"] = Relationship(back_populates="team")

class TeamCreate(TeamBase):
    pass

class TeamPublic(TeamBase):
    pass

class TeamUpdate(SQLModel):
    name: str | None = None
    headquarters: str | None = None

#################### HERO ###########################
class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True) 
    team: Team | None = Relationship(back_populates="heroes")

class HeroCreate(HeroBase):
    pass

class HeroPublic(HeroBase):
    pass

class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None
    team_id: int | None = None

#################### USUARIOS ###########################
class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str | None = None
    full_name: str | None = None
    disabled: bool = False

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str          # nunca "password"

class UserCreate(UserBase):
    password: str                 # entra en texto plano, no se persiste

class UserPublic(UserBase):
    id: int                       # sin hashed_password: no se filtra

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"