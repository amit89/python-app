from jose import JWTError, jwt
from datetime import  datetime, timedelta
from fastapi import status, Depends, HTTPException
from fastapi.security import  OAuth2PasswordBearer
from database import database
from sqlalchemy.orm import Session
from models import models
from app.config import settings
from scehma import  schemas


oauth2_scehme = OAuth2PasswordBearer(tokenUrl = 'login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expired = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expired})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str, credenatials_exception):
    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("user_id")

        if id is None:
            raise credenatials_exception
        token_data = schemas.TokenData(id = id)
    except JWTError:
        raise credenatials_exception
    return token_data


def get_current_user(token: str = Depends(oauth2_scehme), db: Session = Depends(database.get_db)):
    credentails_exception =  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= f"In valid credenatils", headers= {"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentails_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user

