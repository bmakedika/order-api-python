from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBearer
from app.api import products, auth, orders, invoices
from fastapi.middleware.cors import CORSMiddleware
import time
import csv
import os
from datetime import datetime
from app.core.redis_client import get_redis
from fastapi.responses import JSONResponse
from app.api import users

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


@app.middleware('http')
async def rate_limit_middleware(request : Request, call_next):
    path = request.url.path
    protected_prefixes = ('/orders', '/invoices', '/users/me')

    # rate only for protected endpoints
    if not path.startswith(protected_prefixes):
        return await call_next(request)
    
    redis = get_redis()
    client_ip = request.client.host

    # parameters for endpoints family
    if path.startswith('/orders'):
        bucket = 'orders'
        limit = 120
        ttl_seconds = 300
    elif path.startswith('/invoices'):
        bucket = 'invoices'
        limit = 60
        ttl_seconds = 300
    else:
        bucket = 'users_me'
        limit = 30
        ttl_seconds = 300
    
    key = f'rate_limit:{bucket}:{client_ip}'

    current_count = redis.incr(key)
    if current_count == 1:
        redis.expire(key, ttl_seconds)
    if current_count > limit:
        return JSONResponse(
            status_code=429,
            content={'detail': 'Too many requests. Please try again later.'}
        )
    
    return await call_next(request)


@app.get("/")
def home():
    return {'message': 'Order API running'}

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(invoices.router)
app.include_router(users.router)