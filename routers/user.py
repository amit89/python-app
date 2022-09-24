from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from scehma.schemas import PostCreate, PostResponse, CreateUser, UserOut
import psycopg2
from psycopg2.extras import  RealDictCursor
from models import models
from sqlalchemy.orm import Session
from database.database import engine, get_db
from typing import List
from util import utils

router = APIRouter(
    prefix= "/users",
    tags = ['Users'] #creat different section in swagger docs
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def create_user(user: CreateUser ,db: Session = Depends(get_db)):
    #hast the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh((new_user))
    return new_user


@router.get("/{id}", response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise  HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {id} does not exist")
    return user
