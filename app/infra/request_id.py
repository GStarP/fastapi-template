import contextvars
import uuid

request_id_ctx_var = contextvars.ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    return request_id_ctx_var.get()


def set_request_id():
    request_id_ctx_var.set(uuid.uuid4())
