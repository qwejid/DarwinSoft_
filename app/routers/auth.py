from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.depenndencies import get_db
from app.utils.security import verify_password
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from app.schemas import User

load_dotenv()

router = APIRouter(tags=["User"])

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(session: AsyncSession, username: str, password: str):
    user = crud.get_user_by_username(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@router.post(
    "/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED
)
async def register(
    user: schemas.UserCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    db_user = await crud.get_user_by_username(session, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(session=session, user_data=user)


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    session: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await crud.get_user_by_username(session, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/users/<username>')
async def get_user(session: Annotated[AsyncSession, Depends(get_db)], username: str) -> User:
    user = await crud.get_user_by_username(session, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get('/users')
async def get_users(session: Annotated[AsyncSession, Depends(get_db)]) -> list[User]:
    users = await crud.get_users(session)
    return users