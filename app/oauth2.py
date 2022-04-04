from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from . import models, schema
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .config import setting

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# Secret Key in our server only
# Algorithm
# Expiration time after login

SECRET_KEY = setting.SECRET_KEY
ALGORITHM = setting.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = setting.ACCESS_TOKEN_EXPIRE_MINUTES

# Create Access token when user login,
# Payload data will be in dictionary form {"user_id": id}
# Payload + SECRET_KEY will be encoded by ALGORITHM
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_acccess_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_payload: str = payload.get("user_id")
        if id_payload is None:
            raise credentials_exception
        token_data = schema.TokenData(id=id_payload)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Not valid credentials",
        headers={"Authenticate": "Bearer"},
    )

    token = verify_acccess_token(token, credentials_exception)
    user = db.query(models.Users).filter(models.Users.id == token.id).first()

    return user
