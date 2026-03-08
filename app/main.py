from fastapi import FastAPI
from app.api import products

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Order API running"}

app.include_router(products.router)



















