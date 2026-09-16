from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session, select

from .database import engine
from .models import User
# Importamos las constantes de seguridad del router auth
from .routers.auth import SECRET_KEY, ALGORITHM 

# 1. Codigo original
def get_session():    
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# 2. Nueva lógica de Autenticación con el estilo oficial
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def obtener_usuario_actual(
    token: Annotated[str, Depends(oauth2_scheme)], 
    session: SessionDep  
) -> User:
    """
    Dependencia interna que extrae el token del header HTTP,
    lo decodifica y busca al usuario en la Base de Datos.
    """
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificamos el token que viene en el Header HTTP
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credenciales_exception
            
    except jwt.InvalidTokenError:
        raise credenciales_exception

    # Buscamos al usuario usando SQLModel con tu SessionDep
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credenciales_exception
        
    return user

# 3. Creamos el tipo anotado para los endpoints
CurrentUserDep = Annotated[User, Depends(obtener_usuario_actual)]
