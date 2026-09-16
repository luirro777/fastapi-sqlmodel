from datetime import datetime, timedelta, timezone
from typing import Annotated
import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

# Importamos tu dependencia de sesión moderna
from heroes.dependencies import SessionDep
from heroes.models import User, UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# ⚠️ EN PRODUCCIÓN: Estas constantes deberían estar en un archivo .env
SECRET_KEY = "mi_clave_secreta_super_segura_y_larga_12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- 🔒 FUNCIONES AUXILIARES DE SEGURIDAD ---

def hashear_password(password: str) -> str:
    """Transforma la contraseña de texto plano en un Hash ilegible."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la contraseña ingresada con el Hash guardado en la BD."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def crear_jwt_token(data: dict) -> str:
    """Genera la pulsera VIP (JWT) con fecha de expiración."""
    payload = data.copy()
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expiracion})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# --- 🔌 ENDPOINTS ---

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def registrar_usuario(user_in: UserCreate, session: SessionDep):
    """
    Registra un nuevo usuario en el sistema.
    Usa el esquema 'UserCreate' (con password) pero responde con 'UserPublic' (sin password).
    """
    # 1. Validar que el email no esté tomado
    usuario_existente = session.exec(select(User).where(User.email == user_in.email)).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El email ya está registrado."
        )
    
    # 2. Hashear la contraseña y preparar el modelo de la BD
    password_segura = hashear_password(user_in.password)
    nuevo_usuario = User(
        email=user_in.email,
        nombre=user_in.nombre,
        hashed_password=password_segura
    )
    
    # 3. Guardar en la base de datos usando tu SessionDep
    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    session: SessionDep
):
    """
    Endpoint estándar de inicio de sesión.
    OAuth2PasswordRequestForm obliga al cliente (o Swagger) a enviar los datos
    como 'form-data' con los campos obligatorios 'username' (que será el email) y 'password'.
    """
    # 1. Buscar al usuario por el email (que viene en form_data.username)
    usuario = session.exec(select(User).where(User.email == form_data.username)).first()
    
    # 2. Verificar que el usuario exista y que la contraseña coincida
    if not usuario or not verificar_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Email o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Si todo está bien, generar el token JWT y enviarlo
    token = crear_jwt_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}
