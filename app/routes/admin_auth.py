# app/routes/admin_auth.py
from app.config import ADMIN_KEY
from fastapi import Header, HTTPException


def require_admin_key(x_admin_key: str = Header()):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(401, "Unauthorized")
