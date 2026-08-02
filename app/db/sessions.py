# app/db/sessions.py

from app.config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    try:
        session = SessionLocal()
        yield session
    finally:
        session.close()
