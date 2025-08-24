"""
mocule handles database connections
"""
import os
from sqlmodel import SQLModel, create_engine, Session

_engine = None # pylint: disable=invalid-name

def get_engine():
    """
    returns the connection manager for a speified database
    """
    global _engine # pylint: disable=global-statement
    if _engine is None:
        db_url = os.getenv("DBURL")
        if not db_url:
            raise RuntimeError("DBURL not set")
        _engine = create_engine(db_url, echo=False)
    return _engine

def init_db():
    """
    initialized database with tables from SQLModel
    """
    SQLModel.metadata.create_all(get_engine())

def get_session():
    """
    return database session to make queries
    """
    return Session(get_engine())
