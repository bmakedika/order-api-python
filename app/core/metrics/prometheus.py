import time
from typing import Optional
from fastapi import FastAPI, Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'path', 'status'],
)

REQUEST_DURATION_SECONDS = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'path'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)


def _normalize_path(request: Request) -> str:
    route = request.scope.get('route')
    path_format: Optional[str] = getattr(route, 'path', None)
    return path_format or request.url.path

class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        method = request.method
        path = _normalize_path(request)

        start = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.perf_counter() - start
            REQUESTS_TOTAL.labels(method=method, path=path, status=str(status_code)).inc()
            REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration)


def register_prometheus(app: FastAPI) -> None:
    app.add_middleware(PrometheusMetricsMiddleware)

    @app.get('/metrics', include_in_schema=False)
    def metrics():
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)