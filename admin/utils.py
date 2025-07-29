from datetime import datetime, timedelta, UTC

import jwt
from decouple import config
from fastapi import HTTPException
from starlette import status
from starlette.requests import Request
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=config("ACCESS_TOKEN_EXPIRE_MINUTES",cast=int))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config("JWT_SECRET_KEY"), algorithm=config("ALGORITHM"))


async def get_current_user(request: Request):
    from models.models import User
    credentials_exception = (
        HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    ))

    token = request.session.get("access_token")
    if not token: # Token não existe
        return None #raise credentials_exception

    try:
        payload = jwt.decode(token, config("JWT_SECRET_KEY"), algorithms=[config("ALGORITHM")])
    except: # Token inválido
        return None #raise credentials_exception

    if not payload: # decodificação retornou vazio
        return None #raise credentials_exception

    username = payload.get("sub")
    user = User.objects(username=username).first()
    if user is None: # Usuario não existe
        return None #raise credentials_exception

    if not user.active: # Usuario desativado
        return None #raise credentials_exception
    return user


