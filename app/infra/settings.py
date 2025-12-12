import os
from dataclasses import dataclass, fields

from dotenv import load_dotenv

load_dotenv()


def prefix(s: str) -> str:
    return "APP_" + s


@dataclass
class Settings:
    SERVICE_NAME: str = "fastapi-template"
    DEBUG: bool = False
    LOG_PATH: str = "./logs"
    LOG_LEVEL: str = "INFO"

    DB_URL: str = ""
    REDIS_URL: str = ""

    OTLP_URL: str = ""

    def __post_init__(self):
        for k in fields(self):
            v = os.getenv(prefix(k.name))
            if v is not None:
                if k.type is bool:
                    v = v.lower() == "true"
                elif k.type is int:
                    v = int(v)

                setattr(self, k.name, v)


SETTINGS = Settings()

print(f"{SETTINGS.SERVICE_NAME}: settings loaded\n{SETTINGS}")
