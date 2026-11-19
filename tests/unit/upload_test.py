"""Unit tests: no database, no Docker. Run with `pytest tests/unit`."""
import json

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.models.db import Grid
from app.models.dto import GridDTO
from app.services.location import LocationService

client = TestClient(app)  # no `with`: lifespan (migrations) does not run

DATA_DEFINITION = json.dumps({
    "population_key": "Einwohner", "x_column": "x", "y_column": "y",
    "delimiter": ";", "decode": "utf-8",
})


def test_upload_rejects_invalid_grid_json():
    response = client.post(
        "/upload/",
        files={"file": ("test.csv", b"x;y;Einwohner\n", "text/csv")},
        data={"grid": "not json", "data_definition": DATA_DEFINITION},
    )
    assert response.status_code == 400


def test_grid_from_dto():
    grid = Grid.from_dto(GridDTO(name="Zensus", size="1km", srid=3035))
    assert (grid.name, grid.size, grid.srid, grid.id) == ("Zensus", "1km", 3035, None)


def test_location_from_csv_builds_points_in_grid_srid(monkeypatch):
    saved = []
    monkeypatch.setattr(
        "app.repositories.location.LocationRepository.set_bulk_locations",
        lambda locations: saved.extend(locations) or len(locations),
    )
    csv = pd.DataFrame({"x": [4337500], "y": [2689500], "Einwohner": [4]})

    count = LocationService.location_from_csv(
        Grid(id=7, name="Zensus", size="1km", srid=3035), "x", "y", "Einwohner", csv
    )

    assert count == 1
    assert saved[0].grid_id == 7
    assert saved[0].geom == "SRID=3035;POINT(4337500 2689500)"
    assert saved[0].population == 4
