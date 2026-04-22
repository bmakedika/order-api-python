import csv
import os
import time
from datetime import datetime
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, audit_csv_path: str = 'audit_log.csv'):
        super().__init__(app)
        self.audit_csv_path = audit_csv_path

        if not os.path.exists(self.audit_csv_path):
            with open(self.audit_csv_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['requested_at', 'endpoint_name', 'duration_ms', 'status_code'])

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        requested_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        endpoint_name = f'{request.method} {request.url.path}'

        status_code = 200
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            with open(self.audit_csv_path, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([requested_at, endpoint_name, duration_ms, status_code])