import os
import json
import unittest

from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from testcontainers.postgres import PostgresContainer
from fastapi.testclient import TestClient
from app.main import app
from app.log import logger

client = TestClient(app)


class TestGridAPI(unittest.TestCase):

    test_id = None
    test_srid = 3035

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
        # Given
        endpoint = "/grid"
        logger.info(f"test api endpoint {endpoint} to fetch all grids")
        # When
        response = client.get(endpoint)
        # Then
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.json()) == 0)

    def test_upload_population_data(self):
        # Upload
        # Given
        file_path = os.path.join("tests", "resources", "Test_Zensus.csv")
        test_name = "Test Data Zensus 1km"
        grid_payload = {
            "name": test_name,
            "size": "1km",
            "srid": self.test_srid
        }
        data_definition_payload = {
            "population_key": "Einwohner",
            "x_column": "x_mp_1km",
            "y_column": "y_mp_1km",
            "delimiter": ";",
            "decode": "utf-8"
        }

        # When
        with open(file_path, "rb") as f:
            response = client.post(
                "/upload",
                files={"file": ("test.csv", f, "text/csv")},
                data={
                    "grid": json.dumps(grid_payload),
                    "data_definition": json.dumps(data_definition_payload)
                },
            )

        # Then
        self.assertTrue(response.status_code == 200)
        self.test_id = response.json()["id"]
        self.assertTrue(self.test_id == 1)
        self.assertTrue(response.json()["name"] == test_name)

        # Given
        endpoint = "/grid"
        logger.info(f"test api endpoint {endpoint} to fetch all grids")
        # When
        response = client.get(endpoint)
        # Then
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.json()) == 1)

        # Population
        # Given
        polygon_around_test_data = ("POLYGON ((3989527 3589065, 4676576 3588708, "
                                    "4715425 2693702, 3961852 2673737, 3989527 3589065))")
        population_payload = {
            "grid_id": self.test_id,
            "polygon_srid": self.test_srid,
            "polygon": polygon_around_test_data
        }
        endpoint = "/"
        # When
        response = client.request("GET", endpoint, json=population_payload)
        # Then
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()["population"] == 21008)
