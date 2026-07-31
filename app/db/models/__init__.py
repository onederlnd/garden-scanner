# app/db/models/__init__.py
# This file is the model registry.

# New models must be imported here in order
# for them to be loaded into the system.
from app.db.base import Base  # noqa
from app.db.models.plants import Plant  # noqa

models = [Plant]
