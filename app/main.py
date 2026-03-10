from fastapi import FastAPI
from app.api import products, auth

app = FastAPI()

@app.get("/")
def home():
    return {'message': 'Order API running'}

app.include_router(products.router)
app.include_router(auth.router)