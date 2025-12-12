import logging
import os
import socket

from fastapi import FastAPI
from opentelemetry import _logs, baggage, context, metrics, trace
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.tortoiseorm import TortoiseORMInstrumentor
from opentelemetry.processor.baggage import ALLOW_ALL_BAGGAGE_KEYS, BaggageSpanProcessor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .settings import SETTINGS


def init_observable(app: FastAPI):
    if SETTINGS.OTLP_URL == "":
        print(f"{SETTINGS.SERVICE_NAME}: OTLP_URL is empty, skip init_observable")
        return

    resource = Resource.create(
        attributes={
            "service.name": SETTINGS.SERVICE_NAME,
            "service.machine.hostname": socket.gethostname(),
            "service.process.pid": str(os.getpid()),
        }
    )

    """
    Trace
    """
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=SETTINGS.OTLP_URL, insecure=True))
    )
    # 自动将 baggage 传播到后代 span
    trace_provider.add_span_processor(BaggageSpanProcessor(ALLOW_ALL_BAGGAGE_KEYS))
    trace.set_tracer_provider(trace_provider)

    # FastAPI
    # 只 trace 路径包含 `/api/` 的请求
    FastAPIInstrumentor.instrument_app(app=app, excluded_urls="^(?!.*/api/).*")

    # TortoiseORM
    TortoiseORMInstrumentor().instrument()

    # Redis
    RedisInstrumentor().instrument()

    """
    Log
    """
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(endpoint=SETTINGS.OTLP_URL, insecure=True)
        )
    )
    _logs.set_logger_provider(logger_provider)

    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    """
    Metric
    """
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=SETTINGS.OTLP_URL, insecure=True),
                export_interval_millis=5000,
            )
        ],
    )
    metrics.set_meter_provider(meter_provider)

    print(f"{SETTINGS.SERVICE_NAME}: init_observable done")


def set_baggage(key: str, value: str | int | float | bool) -> object:
    ctx = baggage.set_baggage(key, value)
    context.attach(ctx)
    # * baggage 只传播到后代 span，在当前 span 中需要额外设置
    trace.get_current_span().set_attribute(key, value)
    return ctx
