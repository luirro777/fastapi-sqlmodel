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
# Base común para compartir campos
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    nombre: str

# Tabla real en la Base de Datos
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str  # <-- ¡Nunca texto plano!

# Esquema para recibir los datos de registro desde el Frontend
class UserCreate(UserBase):
    password: str

# Esquema para responderle al Frontend (Sin mostrar la contraseña)
class UserPublic(UserBase):
    id: int