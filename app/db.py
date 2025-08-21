# app/db.py
import os
from sqlmodel import SQLModel, create_engine, Session

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv("DBURL")
        if not db_url:
            raise RuntimeError("DBURL not set")
        _engine = create_engine(db_url, echo=False)
    return _engine

def init_db():
    SQLModel.metadata.create_all(get_engine())

def get_session():
    return Session(get_engine())
