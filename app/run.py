import logging

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.features.user import router as user_router
from app.infra import log, observable, orm, request_id
from app.shared import error, rest

app = FastAPI()

# Init Logging
log.init_logging()
logger = logging.getLogger(__name__)
# Init Observable
observable.init_observable(app)

# Init ORM
orm.init_orm(app)


###
# Middleware
###
@app.middleware("http")
async def middleware_request_id(request: Request, call_next):
    client_request_id = request.headers.get("X-Request-ID")
    rid = request_id.set_request_id(client_request_id)
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


@app.exception_handler(Exception)
async def global_exception_handler(_, exc: Exception):
    logger.exception("Exception occurred")

    # 处理业务异常
    if isinstance(exc, error.BizError):
        return JSONResponse(
            status_code=200,
            content=rest.err_ret(code=exc.code, message=exc.message, data=exc.data),
        )

    # 隐藏异常详情
    message = "Internal server error"
    return JSONResponse(
        status_code=200,
        content=rest.err_ret(message=message),
    )


###
# API
###
api_router = APIRouter(prefix="/api")


@api_router.get("/ping")
async def r_ping():
    # * request_id, attr1, attr2 都会被记录为 log_record 属性
    logger.info("ping", extra={"attr1": 1, "attr2": "abc"})
    return rest.ok_ret("pong")


@api_router.get("/err")
async def r_err():
    v = 1 / 0
    return rest.ok_ret("err")


api_router.include_router(router=user_router.router)
app.include_router(router=api_router)
