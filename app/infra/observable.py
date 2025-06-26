import logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.tortoiseorm import TortoiseORMInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .settings import settings


def init_observable(app: FastAPI):
    resource = Resource.create(attributes={"service.name": settings.SERVICE_NAME})

    # 自动 trace 请求响应
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(  # type: ignore
        BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.OTLP_URL, insecure=True))
    )
    # 只 trace url 包含 /api/ 的请求
    FastAPIInstrumentor.instrument_app(app=app, excluded_urls="^(?!.*/api/).*")

    # 自动 trace 数据库操作
    TortoiseORMInstrumentor().instrument()

    # 自动 log
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(endpoint=settings.OTLP_URL, insecure=True)
        )
    )
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)
