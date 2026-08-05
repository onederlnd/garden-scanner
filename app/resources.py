from app.db.models.plants import Plant
from app.schemas.plants import PlantOut, PlantCreate, PlantUpdate

resources = [
    {
        "model": Plant,
        "out_schema": PlantOut,
        "create_schema": PlantCreate,
        "update_schema": PlantUpdate,
        "url_path": Plant.__tablename__,
        "label_field": "common_name",
    }
]
