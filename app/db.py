from __future__ import annotations
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.models.orm import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/db/app.sqlite")

# SQLite threading needs this:
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

def init_db():
    # for quick start we use Base metadata instead of Alembic migrations
    Base.metadata.create_all(bind=engine)
