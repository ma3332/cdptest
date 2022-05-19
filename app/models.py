from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, FLOAT
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

# DB SQL Table Structure is presented as class <name> inherited from Base

# primary_key = True -> SQLAlchemy will automatically set autoincrement=True
class PostForm(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="TRUE", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    # "ForeignKey" is linkage of Tables in DB
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # automatically find the relationship between two tables and return the response of Schema
    # Check schema.PostResponse to understand better
    # this "relationship" is only helpful for Schema only, not the linkage between Tables DB
    user = relationship("Users")


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    phone_number = Column(String, unique=True)


# Composite Key = combination of 2 primary keys
class Votes(Base):
    __tablename__ = "votes"
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    post_id = Column(
        Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )


class CDP(Base):
    __tablename__ = "cdp"
    STT = Column(Integer, primary_key=True)
    depositor = Column(String, nullable=False)
    depositor_pre = Column(String, nullable=False)
    depositor_suf = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    published = Column(Boolean, server_default="False", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
    margin = Column(FLOAT(precision=10, decimal_return_scale=None), nullable=False)
    code = Column(String, nullable=False)


class CDPPayBack(Base):
    __tablename__ = "cdppayback"
    STT = Column(Integer, primary_key=True)
    depositor = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    code = Column(String, nullable=False)
    published = Column(Boolean, server_default="False", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )
