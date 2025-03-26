import os

import pytest

from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.postgres import PostgresContainer
from fastapi.testclient import TestClient

from app.model import *
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="session")
def session(request):
    '''
    Setup postGIS container
    '''
    postgis = PostgresContainer(
        "postgis/postgis:latest",
        "5432",
        "postgres",
        "postgres",
        "population",
    )

    postgis.start()

    os.environ["DBURL"] = postgis.get_connection_url()
    
    engine = create_engine(os.getenv("DBURL"), echo=False)
    session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))

    SQLModel.metadata.create_all(engine)
    
    def stop_db():
        postgis.stop()

    request.addfinalizer(stop_db)

    return session
    
def test_read_main(session):
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
