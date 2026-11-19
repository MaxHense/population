"""Admin upload is protected by the ADMIN_TOKEN env var. No database needed:
every request here is rejected (or fails validation) before the DB is touched."""
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)  # no `with`: lifespan (migrations) does not run

TOKEN = "test-token-0123456789"
GRID = json.dumps({"name": "Zensus", "size": "1km", "srid": 3035})
DATA_DEFINITION = json.dumps({
    "population_key": "Einwohner", "x_column": "x", "y_column": "y",
    "delimiter": ";", "decode": "utf-8",
})


def upload(headers=None, grid=GRID):
    return client.post(
        "/admin/grids",
        files={"file": ("test.csv", b"x;y;Einwohner\n", "text/csv")},
        data={"grid": grid, "data_definition": DATA_DEFINITION},
        headers=headers or {},
    )


def test_admin_is_disabled_when_no_token_configured(monkeypatch):
    monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    assert upload({"Authorization": f"Bearer {TOKEN}"}).status_code == 404


def test_admin_is_disabled_when_token_is_empty(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "")
    assert upload({"Authorization": "Bearer "}).status_code == 404


def test_missing_token_is_rejected(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    assert upload().status_code == 401


@pytest.mark.parametrize("header", [
    f"Bearer {TOKEN}x",
    f"Bearer {TOKEN[:-1]}",
    f"Basic {TOKEN}",
    TOKEN,
])
def test_wrong_token_is_rejected(monkeypatch, header):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    assert upload({"Authorization": header}).status_code == 401


def test_valid_token_passes_auth_and_reaches_validation(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", TOKEN)
    # invalid JSON -> 400 proves the request got past auth (and never hit the DB)
    response = upload({"Authorization": f"Bearer {TOKEN}"}, grid="not json")
    assert response.status_code == 400
