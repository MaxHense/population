import os
import json
import unittest
from unittest import mock

from pyproj import Transformer

from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from testcontainers.community.postgres import PostgresContainer
from fastapi.testclient import TestClient
from app.main import app
from tests.images import POSTGIS_IMAGE
import logging

client = TestClient(app)
logger = logging.getLogger(__name__)
ADMIN_TOKEN = "integration-test-token"


class TestGridAPI(unittest.TestCase):

    test_id = None
    test_srid = 3035

    @classmethod
    def setUpClass(cls):
        # Setup PostGIS container
        cls.postgis = PostgresContainer(
            image=POSTGIS_IMAGE,
            username="postgres",
            password="postgres",
            dbname="population",
            driver="psycopg",
        )
        cls.postgis.start()

        os.environ["DBURL"] = cls.postgis.get_connection_url()
        os.environ["ADMIN_TOKEN"] = ADMIN_TOKEN

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
        file_path = os.path.join(os.path.dirname(__file__), "resources", "Test_Zensus.csv")
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
                "/admin/grids",
                headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
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

        # Population of full test data
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
        response = client.request("POST", endpoint, json=population_payload)
        # Then
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()["population"] == 21008)
        cells = response.json()["cells"]
        self.assertEqual(len(cells), 99)
        self.assertEqual(sum(c["population"] for c in cells), 21008)

        # Too many cells: total still returned, cells left out
        with mock.patch("app.services.location.MAX_CELLS", 50):
            response = client.request("POST", endpoint, json=population_payload)
        self.assertEqual(response.json()["population"], 21008)
        self.assertIsNone(response.json()["cells"])

        # Population of first entry of test data
        # Given
        polygon_around_test_data = ("POLYGON ((4337000 2689000, 4337000 2690000, "
                                    "4338000 2690000, 4338000 2689000, 4337000 2689000))")
        population_payload = {
            "grid_id": self.test_id,
            "polygon_srid": self.test_srid,
            "polygon": polygon_around_test_data
        }
        endpoint = "/"
        # When
        response = client.request("POST", endpoint, json=population_payload)
        # Then
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json()["population"] == 4)
        cells = response.json()["cells"]
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0]["population"], 4)
        # cell square around centre 4337500/2689500 (EPSG:3035), corners as [lat, lng]
        to_wgs84 = Transformer.from_crs(3035, 4326)
        expected = sorted(to_wgs84.transform(y, x) for x, y in [
            (4337000, 2689000), (4337000, 2690000), (4338000, 2690000), (4338000, 2689000)])
        for got, want in zip(sorted(cells[0]["polygon"]), expected):
            self.assertAlmostEqual(got[0], want[0], places=6)
            self.assertAlmostEqual(got[1], want[1], places=6)

        # Polygon between cell centres: 0 people, no cells
        population_payload["polygon"] = ("POLYGON ((4337600 2689600, 4337600 2689900, "
                                         "4337900 2689900, 4337900 2689600, 4337600 2689600))")
        response = client.request("POST", endpoint, json=population_payload)
        self.assertEqual(response.json()["population"], None)
        self.assertEqual(response.json()["cells"], [])
