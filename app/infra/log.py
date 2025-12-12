import logging
import logging.handlers
from pathlib import Path

from opentelemetry import baggage

from .settings import SETTINGS


# 将 baggage 所有属性注入 LogRecord
# 将 action 等自定义属性注入 LogRecord
class LogAttributesFilter(logging.Filter):
    def filter(self, record):
        for key, value in baggage.get_all().items():
            setattr(record, key, value)

        # ! formatter 中使用的属性必须存在
        record.request_id = getattr(record, "request_id", "")
        record.action = getattr(record, "action", "")
        return True


def init_logging():
    log_dir = Path(SETTINGS.LOG_PATH)
    log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(SETTINGS.LOG_LEVEL)
    root_logger.handlers.clear()

    default_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)s - req:%(request_id)s - action:%(action)s - %(message)s"
    )

    file_handler = logging.handlers.TimedRotatingFileHandler(
        str(log_dir / "app.log"),
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.setLevel(SETTINGS.LOG_LEVEL)
    file_handler.setFormatter(default_formatter)
    file_handler.addFilter(LogAttributesFilter())
    root_logger.addHandler(file_handler)

    # log to terminal when debug
    if SETTINGS.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(SETTINGS.LOG_LEVEL)
        console_handler.setFormatter(default_formatter)
        console_handler.addFilter(LogAttributesFilter())
        root_logger.addHandler(console_handler)

    print(f"{SETTINGS.SERVICE_NAME}: init_logging done")


init_logging()
LOGGER = logging.getLogger(SETTINGS.SERVICE_NAME)
