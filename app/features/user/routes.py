from fastapi import APIRouter
from pydantic import BaseModel
from . import models
from app.shared import rest
from typing import Optional

router_user = APIRouter(prefix="/user")


class UserUpdate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


@router_user.post("/")
async def r_update_user(user: UserUpdate):
    if user.id is None:
        if user.name is None:
            return rest.err_ret("missing name")
        u = await models.User.create(name=user.name, password="123456")
        return rest.ok_ret(u.__dict__)
