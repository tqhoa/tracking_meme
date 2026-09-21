# Monitoring & Observability

> Standards for logging, metrics, tracing, alerting, and Grafana dashboard design.

## 🔭 The Three Pillars of Observability

| Pillar      | JS/TS Tool             | Python Tool                 | Purpose                    |
| ----------- | ---------------------- | --------------------------- | -------------------------- |
| **Logs**    | Pino + Loki            | structlog + Loki            | What happened              |
| **Metrics** | prom-client + Grafana  | prometheus-client + Grafana | How the system is behaving |
| **Traces**  | OpenTelemetry + Jaeger | OpenTelemetry + Jaeger      | Why something is slow      |

---

## 📝 Logging Rules

### Log Levels

| Level   | When to Use                                            |
| ------- | ------------------------------------------------------ |
| `error` | Unexpected failure requiring attention                 |
| `warn`  | Unexpected but recoverable situation                   |
| `info`  | Normal significant events (startup, request lifecycle) |
| `debug` | Detailed debugging info (dev only)                     |
| `trace` | Very verbose (never in production)                     |

### Log Format — Structured JSON (always!)

**JavaScript:**

```js
// ✅ Structured log — searchable and parseable
logger.info({
  event: "order.placed",
  orderId: order.id,
  userId: user.id,
  amount: order.total,
  durationMs: Date.now() - startTime,
  requestId: req.id,
});

// ❌ Unstructured log — cannot be queried
console.log(`Order ${orderId} placed by user ${userId}`);
```

**Python:**

```python
# ✅ structlog — structured, bound context
import structlog

logger = structlog.get_logger()

logger.info(
    "order.placed",
    order_id=order.id,
    user_id=user.id,
    amount=float(order.total),
    duration_ms=int((time.monotonic() - start) * 1000),
    request_id=request_id,
)

# ❌ Unstructured
print(f"Order {order_id} placed by user {user_id}")
```

### Mandatory Fields

```json
{
  "level": "info",
  "timestamp": "2026-01-01T00:00:00.000Z",
  "service": "order-service",
  "version": "1.2.3",
  "environment": "production",
  "request_id": "uuid",
  "user_id": "uuid",
  "event": "order.placed",
  "duration_ms": 45
}
```

### What NOT to Log

```
❌ Never log: passwords, tokens, credit card numbers, SSNs, PII
```

### Logger Setup

**JavaScript (Pino):**

```js
// src/utils/logger.js
import pino from "pino";

export const logger = pino({
  level: process.env.LOG_LEVEL || "info",
  base: {
    service: process.env.APP_NAME,
    version: process.env.npm_package_version,
    env: process.env.NODE_ENV,
  },
  timestamp: pino.stdTimeFunctions.isoTime,
});
```

**Python (structlog):**

```python
# shared/utils/logger.py
import logging
import structlog
from shared.config import settings

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger().bind(
    service=settings.app_name,
    environment=settings.environment,
)
```

**FastAPI request logging middleware:**

```python
# api/middleware/logging.py
import time
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)
        start = time.monotonic()

        response = await call_next(request)

        logger.info(
            "http.request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=int((time.monotonic() - start) * 1000),
        )
        structlog.contextvars.clear_contextvars()
        return response
```

---

## 📊 Metrics (Prometheus + Grafana)

### Metric Types

| Type          | Use Case                   | Example                                    |
| ------------- | -------------------------- | ------------------------------------------ |
| **Counter**   | Values that only increase  | `http_requests_total`                      |
| **Gauge**     | Values that go up and down | `active_connections`, `memory_usage_bytes` |
| **Histogram** | Distribution of values     | `http_request_duration_seconds`            |
| **Summary**   | Pre-calculated percentiles | `request_latency_percentiles`              |

### Naming Convention

```
# Pattern: {namespace}_{subsystem}_{name}_{unit}
# All lowercase, underscores, snake_case

http_request_duration_seconds         # histogram
http_requests_total                   # counter
http_requests_in_flight               # gauge
db_query_duration_seconds             # histogram
cache_hits_total                      # counter
cache_misses_total                    # counter
queue_messages_pending                # gauge
queue_processing_duration_seconds     # histogram
payment_transactions_total            # counter (+ status label)
```

### Labels — Don't Use High-Cardinality Values

```
✅ Good labels: method, route, status_code, service
❌ Bad labels: user_id, order_id, session_id  (millions of time series → kills Prometheus)
```

### Metrics Setup

**JavaScript (prom-client + Express):**

```js
// middleware/metrics.js
import client from "prom-client";

const httpDuration = new client.Histogram({
  name: "http_request_duration_seconds",
  help: "Duration of HTTP requests in seconds",
  labelNames: ["method", "route", "status_code"],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
});

export function metricsMiddleware(req, res, next) {
  const end = httpDuration.startTimer();
  res.on("finish", () => {
    end({
      method: req.method,
      route: req.route?.path || req.path,
      status_code: res.statusCode,
    });
  });
  next();
}

app.get("/metrics", async (req, res) => {
  res.set("Content-Type", client.register.contentType);
  res.end(await client.register.metrics());
});
```

**Python (prometheus-client + FastAPI):**

```python
# shared/metrics.py
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'route', 'status_code'],
)
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'route'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
)

# api/middleware/metrics.py
from starlette.middleware.base import BaseHTTPMiddleware

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        response = await call_next(request)
        duration = time.monotonic() - start

        route = request.scope.get("route")
        path = route.path if route else request.url.path

        REQUEST_COUNT.labels(
            method=request.method,
            route=path,
            status_code=response.status_code,
        ).inc()
        REQUEST_DURATION.labels(method=request.method, route=path).observe(duration)
        return response

# Expose metrics endpoint
@app.get("/metrics", include_in_schema=False)
async def metrics():
    from fastapi.responses import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

---

## 📈 Grafana Dashboard Design

### Dashboard Naming

```
# Pattern: {Service} — {Category}
User Service — Overview
User Service — Errors & Latency
Order Service — Business Metrics
Infrastructure — Redis
Infrastructure — PostgreSQL
```

### Panel Naming

```
# Use title case, include units in title
Request Rate (req/s)
P99 Latency (ms)
Error Rate (%)
Active DB Connections
Cache Hit Rate (%)
Queue Depth
Memory Usage (MB)
```

### The RED Method (for Services)

Every service dashboard MUST have these 3 panels:

- **R** — **Rate**: requests per second
- **E** — **Errors**: error rate (%)
- **D** — **Duration**: P50, P95, P99 latency

```promql
# Rate
rate(http_requests_total{service="order-service"}[5m])

# Error rate
rate(http_requests_total{status_code=~"5.."}[5m])
/ rate(http_requests_total[5m]) * 100

# P99 latency (ms)
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket{service="order-service"}[5m])
) * 1000
```

### The USE Method (for Infrastructure)

Every infrastructure dashboard MUST have:

- **U** — **Utilization**: % of resource being used
- **S** — **Saturation**: queue depth, wait time
- **E** — **Errors**: error count/rate

### Standard Dashboard Layout

```
Row 1: Summary / Health Overview (traffic lights)
Row 2: RED metrics (Rate, Errors, Duration)
Row 3: Resource usage (CPU, Memory, DB connections)
Row 4: Business metrics (orders/min, signups, payments)
Row 5: Logs panel (Loki integration)
```

---

## 🚨 Alerting Rules

### Severity Levels

| Level      | Response Time         | Example                        |
| ---------- | --------------------- | ------------------------------ |
| `critical` | Immediate (PagerDuty) | Service down, payment failures |
| `warning`  | Within 30min (Slack)  | High error rate, slow queries  |
| `info`     | Business hours        | Unusual traffic patterns       |

### Standard Alert Rules (Prometheus AlertManager)

```yaml
groups:
  - name: service-alerts
    rules:
      - alert: ServiceDown
        expr: up{job="my-service"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"

      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status_code=~"5.."}[5m])
          / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Error rate > 5% on {{ $labels.service }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency > 1s on {{ $labels.service }}"

      - alert: LowCacheHitRate
        expr: |
          rate(cache_hits_total[5m])
          / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.7
        for: 10m
        labels:
          severity: warning
```

---

## 🔍 Distributed Tracing (OpenTelemetry)

**JavaScript:**

```js
// src/tracing.js
import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { JaegerExporter } from "@opentelemetry/exporter-jaeger";

const sdk = new NodeSDK({
  traceExporter: new JaegerExporter({ endpoint: process.env.JAEGER_ENDPOINT }),
  instrumentations: [getNodeAutoInstrumentations()],
  serviceName: process.env.APP_NAME,
});

sdk.start();
```

**Python:**

```python
# shared/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from shared.config import settings

def setup_tracing(app) -> None:
    provider = TracerProvider()
    provider.add_span_processor(
        BatchSpanProcessor(JaegerExporter(agent_host_name=settings.jaeger_host))
    )
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
```

### Span Naming

```
# HTTP: {method} {route}
GET /api/v1/users/{id}

# DB: {operation} {table}
SELECT users
INSERT orders

# Cache: {operation} {key_pattern}
GET user:{id}
SET session:{id}

# Queue: {operation} {queue_name}
PUBLISH order.placed
CONSUME email.send
```
