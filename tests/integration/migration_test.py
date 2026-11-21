"""Alembic must work on a plain Postgres database where PostGIS is not enabled yet (e.g. fresh Neon)."""
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from testcontainers.community.postgres import PostgresContainer

from tests.images import POSTGIS_IMAGE

ROOT = Path(__file__).parents[2]


@pytest.fixture(scope="module")
def fresh_db_url():
    with PostgresContainer(POSTGIS_IMAGE, driver="psycopg") as pg:
        admin = create_engine(pg.get_connection_url(), isolation_level="AUTOCOMMIT")
        with admin.connect() as conn:
            # template0: PostGIS binaries installed, extension NOT enabled
            conn.execute(text("CREATE DATABASE fresh TEMPLATE template0"))
        admin.dispose()
        yield pg.get_connection_url().rsplit("/", 1)[0] + "/fresh"


def test_upgrade_enables_postgis_on_fresh_database(fresh_db_url, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("DBURL", fresh_db_url)
    engine = create_engine(fresh_db_url)
    with engine.connect() as conn:
        assert conn.scalar(text("SELECT count(*) FROM pg_extension WHERE extname = 'postgis'")) == 0

    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")

    with engine.connect() as conn:
        assert conn.scalar(text("SELECT count(*) FROM pg_extension WHERE extname = 'postgis'")) == 1
    assert {"grid", "location"} <= set(inspect(engine).get_table_names())
    engine.dispose()


def test_upgrade_keeps_existing_cells_and_stores_all_in_epsg_3035(fresh_db_url, monkeypatch):
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("DBURL", fresh_db_url)
    config = Config(str(ROOT / "alembic.ini"))
    command.downgrade(config, "base")
    command.upgrade(config, "fe1e4608e178")  # first schema: size as text, any SRID per row
    engine = create_engine(fresh_db_url)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO grid (id, name, size, srid) VALUES (1, 'Zensus', '1km', 3035)"))
        conn.execute(text("INSERT INTO location (grid_id, geom, population) "
                          "VALUES (1, 'SRID=3035;POINT(4337500 2689500)', 4)"))

    command.upgrade(config, "head")

    with engine.connect() as conn:
        assert conn.execute(text("SELECT name, cell_size_m FROM grid")).one() == ("Zensus", 1000)
        assert conn.execute(text("SELECT ST_AsEWKT(geom), population FROM location")).one() \
            == ("SRID=3035;POINT(4337500 2689500)", 4)
        assert conn.scalar(text("SELECT Find_SRID('public', 'location', 'geom')")) == 3035
    engine.dispose()
