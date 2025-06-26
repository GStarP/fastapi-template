import logging
import logging.handlers
from pathlib import Path

from . import request_id
from .settings import settings


# inject request_id to record
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id.get_request_id()
        return True


def init_logging():
    log_dir = Path(settings.LOG_PATH)
    log_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.handlers.clear()

    default_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(process)d:%(threadName)s:%(thread)d - %(pathname)s:%(lineno)s - req:%(request_id)s - %(message)s"
    )

    file_handler = logging.handlers.TimedRotatingFileHandler(
        str(log_dir / "app.log"),
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.setLevel(settings.LOG_LEVEL)

    file_handler.setFormatter(default_formatter)
    file_handler.addFilter(RequestIDFilter())
    root_logger.addHandler(file_handler)

    # log to terminal when debug
    if settings.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(settings.LOG_LEVEL)
        console_handler.setFormatter(default_formatter)
        console_handler.addFilter(RequestIDFilter())
        root_logger.addHandler(console_handler)
