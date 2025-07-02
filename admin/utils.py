import enum
from datetime import datetime, timedelta, UTC

import jwt


class Role(str, enum.Enum):
    VIEWER = "viewer"
    ADMIN = "admin"

SECRET_KEY = '9c2b916236e54791026f7037d42202b9a4f8aa4986bf6f196605eaaf731ac3e5'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)