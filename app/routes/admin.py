# app/routes/admin.py
from fastapi import FastAPI
from app.routes.crud_factory import CrudFactory

from app.resources import resources


def register_admin_routes(app: FastAPI):
    for resource in resources:
        factory = CrudFactory(
            resource["model"],
            resource["out_schema"],
            resource["create_schema"],
            resource["update_schema"],
        )
        app.include_router(factory.router)
