from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, products, orders, invoices, users
from app.core.redis_client import get_redis
from app.core.middlewares.audit import AuditLoggingMiddleware


app = FastAPI(title='Order API', version='0.2.0')

# Audit logging (writes audit_log.csv for the Streamlit dashboard)
app.add_middleware(AuditLoggingMiddleware, audit_csv_path='audit_log.csv')

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
        'DELETE',
    ],
    allow_headers=[
        'Authorization',
        'Content-Type',
    ],
)


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
            content={'detail': 'Too many requests. Please try again later.'},
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