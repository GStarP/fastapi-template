import uuid
from contextvars import ContextVar

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    return request_id_ctx_var.get()


def set_request_id(s: str | None = None) -> str:
    request_id = str(uuid.uuid4()) if s is None else s
    request_id_ctx_var.set(request_id)
    return request_id
