from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing import Optional, List
from .. import models, schema, oauth2
from ..database import engine, get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta

# tags help catagorized in API docs
router = APIRouter(prefix="/users", tags=["Users"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Hashing Password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify(plainPwd, hashedPwd):
    return pwd_context.verify(plainPwd, hashedPwd)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.UserCreationResponse,
)
async def create_user(user: schema.UserCreation, db: Session = Depends(get_db)):
    hased_pwd = pwd_context.hash(user.password)
    user.password = hased_pwd
    newUser = models.Users(**user.dict())
    db.add(newUser)
    db.commit()
    db.refresh(newUser)  # this equals to RETURNING *
    return newUser


@router.get(
    "/{id}",
    response_model=schema.UserCreationResponse,
)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
    return user


@router.post("/login", response_model=schema.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.Users)
        .filter(models.Users.email == user_credentials.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not valid"},
        )
    if not verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not valid"},
        )
    # create JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = oauth2.create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


"""
# First Way
# However, using this way, we cannot login from localhost:8000/docs, we can only login via postman with JWT added to header
@router.post("/login", response_model=schema.Token)
def login(user_credentials: schema.UserLogin, db: Session = Depends(get_db)):
    user = (
        db.query(models.Users)
        .filter(models.Users.email == user_credentials.email)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not valid"},
        )
    if not verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not valid"},
        )
    # create JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = oauth2.create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
"""

"""
# Second Way
# <OAuth2PasswordRequestForm = Depends()> instead of schema.UserLogin
# this way, <username> will be used as general method, instead of specifying email in schema
# <username> can be email, telephone, whatever it is ...
# remember to change Postman input from "raw" to "form-data"
@router.post("/login")
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.Users)
        .filter(models.Users.email == user_credentials.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not valid"},
        )
    if not verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not valid"},
        )
    # create JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = oauth2.create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
"""
