"""Unit tests: no database, no Docker. Run with `pytest tests/unit`."""
import pandas as pd

from app.models.db import Grid
from app.models.dto import GridDTO
from app.services.location import LocationService


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
