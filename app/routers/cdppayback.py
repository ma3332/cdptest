from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import Optional, List
from .. import models, schema, oauth2
from ..database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import func

# tags help catagorized in API docs
router = APIRouter(prefix="/posts/cdppayback", tags=["CDPPAYBACK"])

# response_model=List[schema....]: return a List of schema -> need to import List from typing lib
@router.get("/", response_model=List[schema.CDPPayBackForm])
async def get_all_cdpsPayBack(db: Session = Depends(get_db)):
    cdps = db.query(models.CDPPayBack).all()
    print(cdps)
    return cdps


# this will make sure that the id we get is integer (like PostForm below)
@router.get(
    "/{stt}", response_model=schema.CDPPayBackForm
)  # Path parameter {id} is a string
async def get_cdpPayBack(stt: int, db: Session = Depends(get_db)):
    cdp = db.query(models.CDPPayBack).filter(models.CDPPayBack.STT == stt).first()
    print(cdp)
    if not cdp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
    return cdp


# need /code/{codecdp}
# Otherwise will fetch /{stt} above
@router.get(
    "/code/{codecdp}", response_model=List[schema.CDPPayBackForm]
)  # Path parameter {code} is a string
async def get_cdpPayBack_code(codecdp: str, db: Session = Depends(get_db)):
    cdp = db.query(models.CDPPayBack).filter(models.CDPPayBack.code == codecdp).all()
    if not cdp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )
    return cdp


@router.get("/code/balance/{codecdp}")
async def get_cdp_code_balance(codecdp: str, db: Session = Depends(get_db)):
    cdp_first = db.query(models.CDP).filter(models.CDP.code == codecdp).first()
    cdp_query = (
        db.query(models.CDP.amount)
        .filter(models.CDP.code == codecdp)
        .group_by(models.CDP.STT)
        .all()
    )
    cdp_payback_query = (
        db.query(models.CDPPayBack.amount)
        .group_by(models.CDPPayBack.STT)
        .filter(models.CDPPayBack.code == codecdp)
        .all()
    )
    if cdp_first == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )

    c_total = 0
    cp_total = 0
    for c in cdp_query:
        c_total += abs(c.amount)

    for cp in cdp_payback_query:
        cp_total += abs(cp.amount)

    c_balance = c_total - cp_total

    return {"message": f"Balance of code {codecdp} is {c_balance}"}


# Get Post Message and put into a pydantic format (Post) which name is "new_post"
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schema.CDPPayBackForm
)
async def create_cdp_payBack(
    new_cdp_payback: schema.CDPPayBackCreate,
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

    cdp_first = (
        db.query(models.CDP).filter(models.CDP.code == new_cdp_payback.code).first()
    )
    cdp_query = (
        db.query(models.CDP.amount)
        .filter(models.CDP.code == new_cdp_payback.code)
        .group_by(models.CDP.STT)
        .all()
    )
    cdp_payback_query = (
        db.query(models.CDPPayBack.amount)
        .group_by(models.CDPPayBack.STT)
        .filter(models.CDPPayBack.code == new_cdp_payback.code)
        .all()
    )

    if cdp_first == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "not found your request"},
        )

    c_total = 0
    cp_total = 0
    for c in cdp_query:
        c_total += abs(c.amount)

    for cp in cdp_payback_query:
        cp_total += abs(cp.amount)

    if cp_total + new_cdp_payback.amount > c_total:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "you are paying back more than the threshold of this code"
            },
        )
    newCDPPaybackFetch = models.CDPPayBack(**new_cdp_payback.dict())
    db.add(newCDPPaybackFetch)
    db.commit()
    db.refresh(newCDPPaybackFetch)  # this equals to RETURNING *
    return newCDPPaybackFetch


@router.put("/{stt}", response_model=schema.CDPPayBackForm)
async def update_cdp_payBack(
    stt: int,
    update_cdp_payback: schema.CDPPackBackUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    updatedCDP = db.query(models.CDPPayBack).filter(models.CDPPayBack.STT == stt)
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
    updatedCDP.update(update_cdp_payback.dict(), synchronize_session=False)
    db.commit()
    return updatedCDP.first()
