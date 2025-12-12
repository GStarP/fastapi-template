from opentelemetry import metrics

meter = metrics.get_meter(__name__)

sleep_concurrency_metric = meter.create_up_down_counter(
    name="sleep_concurrency", unit="1"
)

# * 自定义 buckets（默认为适合请求延迟的 ms 级 buckets）
_SLEEP_LATENCY_BUCKETS = [5, 10, 15, 20, 30]
sleep_latency_metric = meter.create_histogram(
    name="sleep_latency",
    unit="s",
    explicit_bucket_boundaries_advisory=_SLEEP_LATENCY_BUCKETS,
)
