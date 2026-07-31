# app/routes/admin_auth.py

import os
from fastapi import Header, HTTPException

ADMIN_KEY = os.getenv("ADMIN_KEY")


def require_admin_key(x_admin_key: str = Header()):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(401, "Unauthorized")
