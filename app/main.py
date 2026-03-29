from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.api import products, auth, orders, invoices

app = FastAPI(title='Order API', version='0.1.0')

security = HTTPBearer()

@app.get("/")
def home():
    return {'message': 'Order API running'}

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(invoices.router)