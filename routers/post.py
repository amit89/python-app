from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from scehma.schemas import PostCreate, PostResponse, PostOut
from models import models
from sqlalchemy.orm import Session
from sqlalchemy import  func
from database.database import engine, get_db
from typing import List
from auth import oauth2
from typing import Optional


router = APIRouter(
    prefix="/posts", #we don't need to set the path in every router method
    tags = ['Post'] #creat different section in swagger docs
)

@router.get("/",response_model=List[PostOut])
def test_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
               limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    ###posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all() --if we want to show only post to logged-ine user
    ## limit is query paramter whi
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return results


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id)))
    # post = cursor.fetchone()
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f" Asked ID:{id} not found ")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(model: PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" INSERT INTO posts(title, content, published) VALUES (%s, %s, %s) RETURNING *""", (model.title, model.content, model.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id = current_user.id ,**model.dict())
    db.add(new_post)
    db.commit()
    db.refresh((new_post))
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id= %s RETURNING *""", (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    deleted_post = post.first()

    if deleted_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f" Asked ID:{id} not found ")

    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= f"Post belongs to another user")

    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=PostResponse)
def upudate_post(id: int, model: PostCreate, db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts  SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (model.title, model.content, model.published, str(id)) )
    # updated_post = cursor.fetchone()
    # conn.commit()
    updated_post = db.query(models.Post).filter(models.Post.id == id)
    post = updated_post.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f" Asked ID:{id} not found ")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= f"Post belongs to another user")
    updated_post.update(model.dict(), synchronize_session=False)
    db.commit()
    return  updated_post.first()