"""Alembic must work on a plain Postgres database where PostGIS is not enabled yet (e.g. fresh Neon)."""
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from testcontainers.community.postgres import PostgresContainer

ROOT = Path(__file__).parents[2]


@pytest.fixture(scope="module")
def fresh_db_url():
    with PostgresContainer("postgis/postgis:latest", driver="psycopg") as pg:
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
