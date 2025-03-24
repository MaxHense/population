import os

import pytest

from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.postgres import PostgresContainer

from app.model import *

@pytest.fixture(scope="session")
def postgis_container():
    '''
    Setup postGIS container
    '''
    postgres = PostgresContainer(
        "postgis/postgis:17.3.5",
        "postgres",
        "postgres",
        "population",
        "5432"
    )
    with postgres as pg:
        os.environ["DBURL"] = postgres.get_connection_url()
        wait_for_logs(pg, "database system is ready to accept connections", 10)
        yield pg

@pytest.fixture(scope="session")
def db(postgis_container: PostgresContainer):
    '''
    Setup database
    '''
    engine = create_engine(os.getenv("DBURL"), echo=False, future=False)
    SQLModel.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session_instance = session_factory()
    yield session_instance
    session_instance.close()
    engine.dispose()
