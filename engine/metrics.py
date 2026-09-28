from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

MODEL_SCAN_TOTAL = Counter(
    "vajra_model_scan_total",
    "Total model assurance scans performed",
    labelnames=("status",),
)

REQUEST_LATENCY = Histogram(
    "vajra_request_latency_seconds",
    "Request latency in seconds",
    labelnames=("endpoint", "method"),
)

HEALTH_CHECKS = Counter(
    "vajra_health_checks_total",
    "Health-check requests served",
    labelnames=("status",),
)


def render_metrics() -> bytes:
    return generate_latest()
