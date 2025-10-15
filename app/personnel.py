from fastapi import APIRouter, HTTPException
from sqlmodel import Field, SQLModel, Session, select
from typing import Optional, List
from .db import engine

router = APIRouter()


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role_id: Optional[int] = None


class Assignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    project: str


@router.post("/roles")
def create_role(role: Role):
    with Session(engine) as s:
        s.add(role)
        s.commit()
        s.refresh(role)
    return role


@router.post("/users")
def create_user(user: User):
    with Session(engine) as s:
        s.add(user)
        s.commit()
        s.refresh(user)
    return user


@router.post("/assignments")
def assign_user(a: Assignment):
    with Session(engine) as s:
        s.add(a)
        s.commit()
        s.refresh(a)
    return a


@router.get("/users", response_model=List[User])
def list_users():
    with Session(engine) as s:
        return s.exec(select(User)).all()
