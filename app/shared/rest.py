from typing import Any

from pydantic import BaseModel


class Ret(BaseModel):
    code: int
    message: str
    data: Any = None


def ok_ret(data: Any = None) -> dict:
    return Ret(code=200, message="", data=data).model_dump()


def err_ret(message: str, code: int = 400, data=None) -> dict:
    return Ret(code=code, message=message, data=data).model_dump()
