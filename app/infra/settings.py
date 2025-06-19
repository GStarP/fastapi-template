import os
from dotenv import load_dotenv
from dataclasses import dataclass, fields


load_dotenv()


def prefix(s: str) -> str:
    return "APP_" + s


@dataclass
class Settings:
    DEBUG: bool = False
    LOG_PATH: str = "./logs"
    LOG_LEVEL: str = "INFO"

    DB_URL: str = ""
    REDIS_URL: str = ""

    def __post_init__(self):
        for k in fields(self):
            v = os.getenv(prefix(k.name))
            if v is not None:
                if k.type is bool:
                    v = v.lower() == "true"
                elif k.type is int:
                    v = int(v)

                setattr(self, k.name, v)


settings = Settings()

print(f"settings: {settings}")
