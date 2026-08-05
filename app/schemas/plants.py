# app/routes/plants/schema.py

import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional


class PlantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    common_name: str
    scientific_name: Optional[str] = None
    life_cycle: Optional[str] = None
    light_needs: Optional[str] = None
    ph_min: Optional[float] = None
    ph_max: Optional[float] = None
    soil_type: Optional[str] = None
    watering_frequency: Optional[str] = None
    spacing: Optional[str] = None
    planting_season: Optional[str] = None
    days_to_harvest: Optional[str] = None
    common_pests: Optional[str] = None
    common_diseases: Optional[str] = None
    notes: Optional[str] = None


class PlantCreate(BaseModel):
    slug: str
    common_name: str
    scientific_name: Optional[str] = None
    life_cycle: Optional[str] = None
    light_needs: Optional[str] = None
    ph_min: Optional[float] = None
    ph_max: Optional[float] = None
    soil_type: Optional[str] = None
    watering_frequency: Optional[str] = None
    spacing: Optional[str] = None
    planting_season: Optional[str] = None
    days_to_harvest: Optional[str] = None
    common_pests: Optional[str] = None
    common_diseases: Optional[str] = None
    notes: Optional[str] = None


class PlantUpdate(BaseModel):
    slug: Optional[str] = None
    common_name: Optional[str] = None
    scientific_name: Optional[str] = None
    life_cycle: Optional[str] = None
    light_needs: Optional[str] = None
    ph_min: Optional[float] = None
    ph_max: Optional[float] = None
    soil_type: Optional[str] = None
    watering_frequency: Optional[str] = None
    spacing: Optional[str] = None
    planting_season: Optional[str] = None
    days_to_harvest: Optional[int] = None
    common_pests: Optional[str] = None
    common_diseases: Optional[str] = None
    notes: Optional[str] = None
