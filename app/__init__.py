import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.infra import log, request_id
from app.shared import rest, error


###
# Init
###
log.init_logging()

logger = logging.getLogger(__name__)
app = FastAPI()


###
# Middleware
###
@app.middleware("http")
async def add_request_id(request, call_next):
    # add request_id for each request
    request_id.set_request_id()
    return await call_next(request)


@app.exception_handler(Exception)
async def custom_exception_handler(_, exc: Exception):
    # log for each error
    logger.error("Exception occurred", exc_info=True)

    # handle business error
    if isinstance(exc, error.BizError):
        return JSONResponse(
            status_code=200,
            content=rest.err_ret(code=exc.code, message=exc.message, data=exc.data),
        )

    # hide detail for other error
    message = "Internal server error"
    return JSONResponse(
        status_code=200,
        content=rest.err_ret(message=message),
    )


###
# API
###
@app.get("/ping")
async def r_ping():
    logger.info("ping")
    return rest.ok_ret("pong")
