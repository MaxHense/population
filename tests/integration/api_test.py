"""POST / against a real PostGIS. Data is put in with SQL, the way the import scripts do it."""
import csv
from pathlib import Path
from unittest import mock

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pyproj import Geod, Transformer
from sqlalchemy import create_engine, text
from testcontainers.community.postgres import PostgresContainer

from app.main import app
from tests.images import POSTGIS_IMAGE

ROOT = Path(__file__).parents[2]
ZENSUS = Path(__file__).parent / "resources" / "Test_Zensus.csv"  # 99 cells, 21008 people, EPSG:3035
LONDON_CELLS = [(530500, 180500, 100), (531500, 180500, 50)]       # British National Grid, EPSG:27700


@pytest.fixture(scope="module")
def client(monkeypatch_module):
    with PostgresContainer(POSTGIS_IMAGE, driver="psycopg") as pg:
        monkeypatch_module.setenv("DBURL", pg.get_connection_url())
        monkeypatch_module.chdir(ROOT)
        command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
        engine = create_engine(pg.get_connection_url())
        with engine.begin() as conn, ZENSUS.open(encoding="utf-8") as file:
            conn.execute(text("INSERT INTO grid (id, name, cell_size_m, srid) VALUES "
                              "(1, 'Zensus', 1000, 3035), (2, 'UK', 1000, 27700)"))
            conn.execute(
                text("INSERT INTO location (grid_id, geom, population) "
                     "VALUES (1, ST_SetSRID(ST_MakePoint(:x, :y), 3035), :p)"),
                [{"x": float(r["x_mp_1km"]), "y": float(r["y_mp_1km"]), "p": int(r["Einwohner"])}
                 for r in csv.DictReader(file, delimiter=";")],
            )
            # a grid in another CRS: the import moves its cells to EPSG:3035
            conn.execute(
                text("INSERT INTO location (grid_id, geom, population) "
                     "VALUES (2, ST_Transform(ST_SetSRID(ST_MakePoint(:x, :y), 27700), 3035), :p)"),
                [{"x": x, "y": y, "p": p} for x, y, p in LONDON_CELLS],
            )
        engine.dispose()
        yield TestClient(app)


@pytest.fixture(scope="module")
def monkeypatch_module():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


def count(client, polygon, srid=3035):
    response = client.post("/", json={"polygon_srid": srid, "polygon": polygon})
    assert response.status_code == 200
    return response.json()


AROUND_ZENSUS = ("POLYGON ((3989527 3589065, 4676576 3588708, "
                 "4715425 2693702, 3961852 2673737, 3989527 3589065))")


def test_population_and_cells_inside_polygon(client):
    result = count(client, AROUND_ZENSUS)
    assert result["population"] == 21008
    assert len(result["cells"]) == 99
    assert sum(c["population"] for c in result["cells"]) == 21008


def test_too_many_cells_returns_total_without_cells(client):
    with mock.patch("app.services.location.MAX_CELLS", 50):
        result = count(client, AROUND_ZENSUS)
    assert result["population"] == 21008
    assert result["cells"] is None


def test_one_cell_with_its_square(client):
    result = count(client, "POLYGON ((4337000 2689000, 4337000 2690000, "
                           "4338000 2690000, 4338000 2689000, 4337000 2689000))")
    assert result["population"] == 4
    [cell] = result["cells"]
    assert cell["population"] == 4
    # square around the centre 4337500/2689500 (EPSG:3035), corners as [lat, lng]
    to_wgs84 = Transformer.from_crs(3035, 4326)
    expected = sorted(to_wgs84.transform(y, x) for x, y in [
        (4337000, 2689000), (4337000, 2690000), (4338000, 2690000), (4338000, 2689000)])
    for got, want in zip(sorted(cell["polygon"]), expected):
        assert got == pytest.approx(want, abs=1e-6)


def test_polygon_between_cell_centres_counts_nobody(client):
    result = count(client, "POLYGON ((4337600 2689600, 4337600 2689900, "
                           "4337900 2689900, 4337900 2689600, 4337600 2689600))")
    assert result == {"population": None, "cells": []}


def test_grid_from_another_crs_is_found_with_wgs84_polygon(client):
    london = "POLYGON ((-0.2 51.45, 0 51.45, 0 51.55, -0.2 51.55, -0.2 51.45))"
    result = count(client, london, srid=4326)
    assert result["population"] == 150
    assert len(result["cells"]) == 2
    (lat1, lng1), (lat2, lng2) = result["cells"][0]["polygon"][:2]
    _, _, side = Geod(ellps="WGS84").inv(lng1, lat1, lng2, lat2)
    assert side == pytest.approx(1000, abs=20)  # drawn in the size of its grid


def test_one_query_sums_all_grids(client):
    europe = "POLYGON ((-5 44, 20 44, 20 58, -5 58, -5 44))"
    assert count(client, europe, srid=4326)["population"] == 21008 + 150
