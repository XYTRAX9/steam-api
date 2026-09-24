from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from app.config import BACKEND_DIR, settings

database_url = make_url(settings.database_url)
if database_url.drivername != "sqlite":
    raise ValueError("Only SQLite databases are supported")
if database_url.database and database_url.database != ":memory:" and not Path(database_url.database).is_absolute():
    database_url = database_url.set(database=str(BACKEND_DIR / database_url.database))

engine = create_engine(database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
