from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from .settings import settings


# TODO: test concurrency
# TODO: connection pool config
def init_orm(app: FastAPI):
    register_tortoise(
        app=app,
        config={
            "connections": {"default": settings.DB_URL},
            "apps": {
                "models": {
                    "models": ["app.features.user.models"],
                    "default_connection": "default",
                }
            },
            "use_tz": True,
            "timezone": "Asia/Shanghai",
        },
        generate_schemas=True,
        add_exception_handlers=True,
    )
