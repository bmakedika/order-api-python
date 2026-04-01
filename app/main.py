from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.api import products, auth, orders, invoices
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Order API', version='0.1.0')

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


@app.get("/")
def home():
    return {'message': 'Order API running'}

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(invoices.router)