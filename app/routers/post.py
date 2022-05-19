from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import Optional, List
from .. import models, schema, oauth2
from ..database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import func

# tags help catagorized in API docs
router = APIRouter(prefix="/posts", tags=["Posts"])

# response_model=List[schema....]: return a List of schema -> need to import List from typing lib
@router.get("/", response_model=List[schema.PostwVoteCount])
async def get_posts_with_votes(
    db: Session = Depends(get_db),
):
    posts = db.query(models.PostForm).all()
    # without "isouter=True", "join" is automatically set up as LEFT INNER JOIN
    posts_votes_count = (
        db.query(models.PostForm, func.count(models.Votes.post_id).label("count_votes"))
        .join(models.Votes, models.Votes.post_id == models.PostForm.id, isouter=True)
        .group_by(models.PostForm.id)
        .all()
    )
    print(type(posts_votes_count))
    return posts_votes_count


# http://127.0.0.1:8000/posts?Limit=5&skip=1&search=34 -> filter of search for all posts
@router.get("/", response_model=List[schema.PostResponse])
async def get_posts(
    db: Session = Depends(get_db),
    Limit: int = 3,
    skip: int = 0,
    search: Optional[str] = None,
):
    posts = (
        db.query(models.PostForm)
        .filter(models.PostForm.title.contains(search))
        .limit(Limit)
        .offset(skip)
        .all()
    )
    print(posts)
    return posts


# this will make sure that the id we get is integer (like PostForm below)
@router.get(
    "/{id}", response_model=schema.PostwVoteCount
)  # Path parameter {id} is a string
async def get_post(id: int, db: Session = Depends(get_db)):
    posts_votes_count = (
        db.query(models.PostForm, func.count(models.Votes.post_id).label("count_votes"))
        .join(models.Votes, models.Votes.post_id == models.PostForm.id, isouter=True)
        .group_by(models.PostForm.id)
        .filter(models.PostForm.id == id)
        .first()
    )
    print(posts_votes_count)
    if not posts_votes_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
    return posts_votes_count


# Get Post Message and put into a pydantic format (Post) which name is "new_post"
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schema.PostResponse
)
async def create_posts(
    new_post: schema.PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    # --- Create a Post ---
    # PostCreate of Schema must compatible with PostForm in models
    # change schema to dict by <**new_post.dict()>
    # newPostFetch is actually a SQL object
    # --- Response to a post creation ---
    # models.PostForm() is actually the SQL form, not dictionary form
    # however, remember that Schema always works with dictionary form
    # in order for "response_model" response correctly (as newPostFetch is actually a SQL object) ->
    # need to add "class Config: orm_mode = True" to schema classes which are applied to response_model
    print(current_user.email)
    newPostFetch = models.PostForm(user_id=current_user.id, **new_post.dict())
    db.add(newPostFetch)
    db.commit()
    db.refresh(newPostFetch)  # this equals to RETURNING *
    return newPostFetch


# when we delete a post, we dont want to return anything, hence only return Response(status_code)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    deletePost = db.query(models.PostForm).filter(models.PostForm.id == id)
    if deletePost.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
    if deletePost.first().user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "you are not allowed"},
        )
    deletePost.delete(synchronize_session=False)
    db.commit()
    # We dont return anything for delete post
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schema.PostResponse)
async def update_post(
    id: int,
    update_post: schema.PostUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    updatedPost = db.query(models.PostForm).filter(models.PostForm.id == id)
    if updatedPost.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
    if updatedPost.first().user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "you are not allowed"},
        )
    updatedPost.update(update_post.dict(), synchronize_session=False)
    db.commit()
    return updatedPost.first()
