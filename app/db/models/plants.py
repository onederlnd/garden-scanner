# app/db/models/plants.py

import uuid
from sqlalchemy.orm import mapped_column, Mapped
from db.base import Base


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, nullable=False
    )
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)
    common_name: Mapped[str] = mapped_column(nullable=False)
    scientific_name: Mapped[str] = mapped_column(nullable=True)
    life_cycle: Mapped[str] = mapped_column(nullable=True)
    light_needs: Mapped[str] = mapped_column(nullable=True)
    ph_min: Mapped[float] = mapped_column(nullable=True)
    ph_max: Mapped[float] = mapped_column(nullable=True)
    soil_type: Mapped[str] = mapped_column(nullable=True)
    watering_frequency: Mapped[str] = mapped_column(nullable=True)
    spacing: Mapped[str] = mapped_column(nullable=True)
    planting_season: Mapped[str] = mapped_column(nullable=True)
    days_to_harvest: Mapped[int] = mapped_column(nullable=True)
    common_pests: Mapped[str] = mapped_column(nullable=True)
    common_diseases: Mapped[str] = mapped_column(nullable=True)
    notes: Mapped[str] = mapped_column(nullable=True)
