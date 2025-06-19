from contextvars import ContextVar
import uuid

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    return request_id_ctx_var.get()


def set_request_id():
    request_id_ctx_var.set(uuid.uuid4().hex)
