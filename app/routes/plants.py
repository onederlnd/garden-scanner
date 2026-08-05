# app/routes/plants.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.templating import templates
from app.schemas import PlantOut
from app.db.models.plants import Plant
from app.db.session import get_db

router = APIRouter(prefix="/plants")


@router.get("/")
def get_list_route(request: Request, db: Session = Depends(get_db)):
    result = db.execute(select(Plant)).scalars().all()
    return templates.TemplateResponse(request, "directory.html", {"plants": result})


@router.get("/{slug}")
def get_plant_route(slug: str, request: Request, db: Session = Depends(get_db)):
    result = db.execute(select(Plant).where(Plant.slug == slug)).scalars().one_or_none()
    if result is None:
        return templates.TemplateResponse(
            request, "not_found.html", {}, status_code=404
        )

    return templates.TemplateResponse(request, "plant_detail.html", {"plant": result})
