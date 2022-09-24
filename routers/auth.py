from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from database import database
from scehma.schemas import UserLogin
from models import models
from util import utils
from auth import oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from  scehma import schemas

router = APIRouter(tags = ['Authentication'])

#OAuth2PasswordRequestForm retrun dict {"username": our username which is email id in this case, "Password": "our password"}
#also instaesd of using OAuth2PasswordRequestForm we can use our SCHEMA ie.e USERLogin as well in that case we need to chnage username with Email.


@router.post('/login', response_model= schemas.Token)
def login( user_credentails: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentails.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_NOT_FOUND, detail= f"Invalid credentaials")

    if not utils.verify(user_credentails.password, user.password):
        raise  HTTPException(status_code=status.HTTP_403_NOT_FOUND, detail=f"Invalid credentails")

    access_token =oauth2.create_access_token(data = {"user_id": user.id})
    return  {"token": access_token, "token_type": "bearer"}




