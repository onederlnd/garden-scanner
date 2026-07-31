# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.admin import register_admin_routes
from app.routes import routers

app = FastAPI()

app.mount("/static", app=StaticFiles(directory="app/static"), name="static")

for router in routers:
    app.include_router(router)

register_admin_routes(app)
