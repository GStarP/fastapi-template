from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.shared import rest

from . import models

router = APIRouter(prefix="/user")


class UserUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


@router.post("/")
async def r_update_user(user: UserUpdate):
    if user.id is None:
        if user.name is None:
            return rest.err_ret("missing name")
        u = await models.User.create(name=user.name, password="123456")
        return rest.ok_ret(u.__dict__)


class UserVO(BaseModel):
    id: str
    name: str


@router.get("/")
async def r_get_user():
    users = await models.User.all()
    return rest.ok_ret([UserVO(id=str(u.id), name=u.name) for u in users])
