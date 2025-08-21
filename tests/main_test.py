import os
import unittest

from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer
from fastapi.testclient import TestClient
from app.main import app
from app.log import logger

client = TestClient(app)

class TestGridAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup PostGIS container
        cls.postgis = PostgresContainer(
            image="postgis/postgis:latest",
            username="postgres",
            password="postgres",
            dbname="population",
        )
        cls.postgis.start()

        os.environ["DBURL"] = cls.postgis.get_connection_url()

        cls.engine = create_engine(os.environ["DBURL"], echo=False)
        cls.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=cls.engine))
        SQLModel.metadata.create_all(cls.engine)
        
        logger.info(f"db is up and current connection url: {cls.postgis.get_connection_url()}")

    @classmethod
    def tearDownClass(cls):
        cls.postgis.stop()
        
    def test_get_all_grids(self):
        #Given
        endpoint = "/grid"
        logger.info(f"test api endpoint {endpoint} to fetch all grids")
        #When
        response = client.get(endpoint)
        #Then
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.json()) == 0)
