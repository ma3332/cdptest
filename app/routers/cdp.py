from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import Optional, List
from .. import models, schema, oauth2
from ..database import engine, get_db
from sqlalchemy.orm import Session

# tags help catagorized in API docs
router = APIRouter(prefix="/posts/cdp", tags=["CDP"])

# response_model=List[schema....]: return a List of schema -> need to import List from typing lib
@router.get("/", response_model=List[schema.CDPForm])
async def get_all_cdps(db: Session = Depends(get_db)):
    cdps = db.query(models.CDP).all()
    print(cdps)
    return cdps


# this will make sure that the id we get is integer (like PostForm below)
@router.get("/{stt}", response_model=schema.CDPForm)  # Path parameter {id} is a string
async def get_cdp(stt: int, db: Session = Depends(get_db)):
    cdp = db.query(models.CDP).filter(models.CDP.STT == stt).first()
    print(cdp)
    if not cdp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
    return cdp


# Get Post Message and put into a pydantic format (Post) which name is "new_post"
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.CDPForm)
async def create_cdp(
    new_cdp: schema.CDPCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    # --- Create a Post ---
    # PostCreate of Schema must compatible with PostForm in models
    # change schema to dict by <**new_post.dict()>
    # newCDPFetch is actually a SQL object
    # --- Response to a post creation ---
    # models.PostForm() is actually the SQL form, not dictionary form
    # however, remember that Schema always works with dictionary form
    # in order for "response_model" response correctly (as newCDPFetch is actually a SQL object) ->
    # need to add "class Config: orm_mode = True" to schema classes which are applied to response_model
    if current_user.email != "tuananh1@example.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "you are not allowed"},
        )
    newCDPFetch = models.CDP(**new_cdp.dict())
    db.add(newCDPFetch)
    db.commit()
    db.refresh(newCDPFetch)  # this equals to RETURNING *
    return newCDPFetch


@router.put("/{stt}", response_model=schema.CDPForm)
async def update_cdp(
    stt: int,
    update_cdp: schema.CDPUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    updatedCDP = db.query(models.CDP).filter(models.CDP.STT == stt)
    if updatedCDP.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
    if current_user.email != "tuananh1@example.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "you are not allowed"},
        )
    updatedCDP.update(update_cdp.dict(), synchronize_session=False)
    db.commit()
    return updatedCDP.first()
