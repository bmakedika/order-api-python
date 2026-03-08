from fastapi import Header, HTTPException
import os

# Auth

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

def require_admin(x_api_key: str = Header()):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")