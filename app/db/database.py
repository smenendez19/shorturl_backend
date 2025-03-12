# Database connection

# Imports
import os

from sqlmodel import Session, create_engine

from app.utils.get_settings import get_settings

settings = get_settings()

os.makedirs("database", exist_ok=True)

# SQLite database
engine = create_engine(settings.db_uri, echo=False)


def get_session():
    with Session(engine) as session:
        yield session
