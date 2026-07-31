# app/routes/admin.py
from fastapi import FastAPI

from app.db.models.plants import Plant
from app.routes.plants.schema import PlantOut, PlantCreate, PlantUpdate
from app.routes.crud_factory import CrudFactory

model_registry = [
    (Plant, PlantOut, PlantCreate, PlantUpdate),
]


def register_admin_routes(app: FastAPI):
    for model, out_schema, create_schema, update_schema in model_registry:
        factory = CrudFactory(model, out_schema, create_schema, update_schema)
        app.include_router(factory.router)
