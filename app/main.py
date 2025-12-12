from asyncio import sleep
from uuid import uuid4

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from opentelemetry import trace

from app.features.metrics.sleep import sleep_concurrency_metric, sleep_latency_metric
from app.features.user import router as user_router
from app.infra import observable, orm
from app.infra.log import LOGGER
from app.infra.redis import REDIS, build_redis_key
from app.shared import error, rest

app = FastAPI()

observable.init_observable(app)
orm.init_orm(app)

"""
Middleware
"""


@app.middleware("http")
async def middleware_request_id(request: Request, call_next):
    client_request_id = request.headers.get("X-Request-ID")
    request_id = client_request_id or uuid4().hex
    observable.set_baggage("request_id", request_id)
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(_, exc: Exception):
    LOGGER.exception("Exception occurred")

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
        content=rest.err_ret(code=403, message=message),
    )


"""
API
"""
api_router = APIRouter(prefix="/api")


@api_router.get("/ping")
async def r_ping():
    import random

    LOGGER.info("ping", extra={"action": "ping", "attr.int": 1})

    tracer = trace.get_tracer(__name__)
    sleep_concurrency_metric.add(1)
    try:
        with tracer.start_as_current_span("sleep"):
            sleep_time = random.randint(5, 30)
            await sleep(sleep_time)
            sleep_latency_metric.record(sleep_time)
    finally:
        sleep_concurrency_metric.add(-1)

    return rest.ok_ret("pong")


@api_router.get("/err")
async def r_err():
    v = 1 / 0
    return rest.ok_ret("err")


@api_router.get("/redis")
async def r_redis():
    v = await REDIS.incr(build_redis_key("count"))
    return rest.ok_ret(v)


# 引入其它模块路由
api_router.include_router(router=user_router.router)
app.include_router(router=api_router)
