from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBearer
from app.api import products, auth, orders, invoices
from fastapi.middleware.cors import CORSMiddleware
import time
import csv
import os
from datetime import datetime

app = FastAPI(title='Order API', version='0.2.0')

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
        'http://localhost:8000',
    ],
    allow_credentials=True,
    allow_methods=[
        'GET', 
        'POST',
        'PUT',
        'PATCH', 
        'DELETE'
    ],
    allow_headers=[
        'Authorization',
        'Content-Type'
    ],
)


@app.middleware('http')
async def logging_middleware(request : Request, call_next):
    if not os.path.exists('audit_log.csv'):
        with open('audit_log.csv', mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['requested_at', 'endpoint_name', 'duration_ms', 'status_code'])
    
    start_time = time.perf_counter()
    requested_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    endpoint_name = f'{request.method} {request.url.path}'
    status_code = 200

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except HTTPException as e:
        status_code = e.status_code
        raise e
    except Exception as e:
        status_code = 500
        raise e
    finally:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        with open('audit_log.csv', mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([requested_at, endpoint_name, duration_ms, status_code])

@app.get("/")
def home():
    return {'message': 'Order API running'}

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(invoices.router)