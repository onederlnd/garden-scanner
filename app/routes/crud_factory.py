# app/routes/crud_factory.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.sessions import get_db
from app.routes.admin_auth import require_admin_key


class CrudFactory:
    def __init__(self, model, out_schema, create_schema, update_schema):
        self.model = model

        self.out_schema = out_schema
        self.create_schema = create_schema
        self.update_schema = update_schema

        self.router = APIRouter(
            prefix=f"/admin/{model.__tablename__}",
            dependencies=[Depends(require_admin_key)],
        )
        self.router.get("/", response_model=list[out_schema])(self.get_list)
        self.router.get("/{id}", response_model=out_schema)(self.get_by_id)
        self.router.post("/", response_model=out_schema)(self.create)
        self.router.patch("/{id}", response_model=out_schema)(self.update)
        self.router.delete("/{id}")(self.delete)

    # in: model class
    def get_list(self, db: Session = Depends(get_db)):
        return db.execute(select(self.model)).scalars().all()

    def get_by_id(self, id, db: Session = Depends(get_db)):
        result = (
            db.execute(select(self.model).where(self.model.id == id))
            .scalars()
            .one_or_none()
        )
        if result is None:
            raise HTTPException(404, "Result not found")

        return result

    def create(self, payload, db: Session = Depends(get_db)):
        obj = self.model(**payload)

        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj

    def update(self, id, payload, db: Session = Depends(get_db)):
        result = (
            db.execute(select(self.model).where(self.model.id == id))
            .scalars()
            .one_or_none()
        )

        if result is None:
            raise HTTPException(404, "Result not found")

        for item, value in payload.items():
            setattr(result, item, value)

        db.commit()
        db.refresh(result)

        return result

    def delete(self, id, db: Session = Depends(get_db)):
        result = (
            db.execute(select(self.model).where(self.model.id == id))
            .scalars()
            .one_or_none()
        )
        if result is None:
            raise HTTPException(404, "Result not found")

        db.delete(result)
        db.commit()
