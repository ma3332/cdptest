from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

# this is the pydantic model (Schema Models), that forces user to input correct data form for PUT and DELETE
# this can also be used to force the response from FastAPI to user
# REMEMBER THAT SCHEMA WORKS WITH DICTIONARY FORM

# FORM THAT USERS INTERACT WITH API


class PostForm(BaseModel):
    title: str
    content: str
    published: bool = True

    class Config:
        orm_mode = True


class UsersForm(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class PostCreate(PostForm):
    pass


class PostUpdate(PostForm):
    pass


class PostResponse(PostForm):
    created_at: datetime
    user_id: int
    user: UsersForm

    class Config:
        orm_mode = True


class PostwVoteCount(BaseModel):
    PostInfo: PostResponse
    count_votes: int

    class Config:
        orm_mode = True


class UserCreation(BaseModel):
    email: EmailStr
    password: str


class UserCreationResponse(BaseModel):
    id: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserLogin(UserCreation):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: int


class CDPForm(BaseModel):
    STT: int
    depositor: str
    depositor_pre: str
    depositor_suf: str
    amount: int
    margin: float
    code: str
    published: bool = False
    created_at: datetime

    class Config:
        orm_mode = True


class CDPCreate(BaseModel):
    depositor: str
    depositor_pre: str
    depositor_suf: str
    amount: int
    margin: float
    code: str
    published: bool = False

    @validator("margin")
    def check_margin(cls, m):
        if m > 1 or m < 0:
            raise ValueError("value must <= 1 or > 0")
        return m

    @validator("code")
    def check_code(cls, c):
        if len(c) < 8:
            raise ValueError("Not Correct code")
        return c


class CDPUpdate(BaseModel):
    published: bool = False


class CDPPayBackForm(BaseModel):
    STT: int
    depositor: str
    amount: int
    code: str
    published: bool = False
    created_at: datetime

    class Config:
        orm_mode = True


class CDPPayBackCreate(BaseModel):
    depositor: str
    amount: int
    code: str
    created_at: datetime
    published: bool = False


class CDPPackBackUpdate(CDPUpdate):
    pass
