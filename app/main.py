from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.api import products, auth

app = FastAPI(title='Order API', version='0.1.0')

security = HTTPBearer()

@app.get("/")
def home():
    return {'message': 'Order API running'}

app.include_router(auth.router)
app.include_router(products.router)