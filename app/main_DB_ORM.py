from fastapi import FastAPI, Response, status, HTTPException, Depends
from typing import Optional, List
from . import models, schema
from .database import engine, get_db
from sqlalchemy.orm import Session
from .routers import post, user, vote, cdp, cdppayback
from .config import setting
from fastapi.middleware.cors import CORSMiddleware

# As we install alembic, we dont need this line anymore
# From now, we will update our table in SQL from alembic
# without alembic, we will run this line below, the purpose of this line code is to create a table in our SQL whenever
# we create a new class in our Models
# However, sqlalchemy orm cannot perform table migration

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# origins = ["https://www.google.com"] : allow access our API from google.com only

# [CORS] All domains can access our API, otherwise CORS will prevent domains from different sources access our API
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)

app.include_router(user.router)

app.include_router(vote.router)

app.include_router(cdp.router)

app.include_router(cdppayback.router)


@app.get("/")
async def wellcome():
    return {"message": "hello hello"}
