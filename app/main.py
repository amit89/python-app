from fastapi import FastAPI
from models import models
from database.database import engine
from routers import post, user, auth, vote
from .config import settings


models.Base.metadata.create_all(bind=engine)

print(settings.database_hostname)
app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message" : "You are calling get api!!!!"}







