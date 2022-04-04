from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import schema, models, oauth2
from ..database import engine, get_db
from sqlalchemy.orm import Session

# tags help catagorized in API docs
router = APIRouter(prefix="/votes", tags=["Votes"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    new_vote: schema.Vote,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post_query_check = db.query(models.PostForm).filter(
        models.Votes.post_id == new_vote.post_id
    )
    if post_query_check.first() == None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Post ID does not exist"},
        )

    voteQuery = db.query(models.Votes).filter(
        models.Votes.post_id == new_vote.post_id,
        models.Votes.user_id == current_user.id,
    )
    if new_vote.dir == 1:
        if voteQuery.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": f"user with id {current_user.id} already votes on post {new_vote.post_id}"
                },
            )
        else:
            updateVoteSQL = models.Votes(
                post_id=new_vote.post_id, user_id=current_user.id
            )
            db.add(updateVoteSQL)
            db.commit()
            return {"message": "Vote Successfully"}
    else:
        if voteQuery.first() == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "not found your undo vote"},
            )
        else:
            voteQuery.delete()
            db.commit()
            return {"message": "Delete Vote Successfully"}
