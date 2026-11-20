"""
module holds the service for locations
"""
import json
import re

from pandas import DataFrame

from app.repositories.location import LocationRepository
from app.models.db import Grid, Location


MAX_CELLS = 2000  # more cells are not sent to the browser, the total is still returned

_SIZE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(km|m)\s*$", re.IGNORECASE)


def cell_size_m(size: str) -> float:
    """'1km' -> 1000, '100m' -> 100"""
    match = _SIZE.match(size)
    if not match:
        raise ValueError(f"Unknown cell size '{size}', expected e.g. '1km' or '100m'")
    value = float(match[1])
    return value * 1000 if match[2].lower() == "km" else value


def _square(geojson: str) -> list[list[float]]:
    ring = json.loads(geojson)["coordinates"][0][:-1]
    return [[lat, lng] for lng, lat in ring]


class LocationService:
    """
    this class is the service for locations
    """
    @staticmethod
    def get_population_by_polygon(grid: Grid, polygon: str, polygon_srid: int):
        """
        returns population of specified polygon
        """
        return LocationRepository.get_population_by_polygon(grid, polygon, polygon_srid)

    @staticmethod
    def get_cells_by_polygon(grid: Grid, polygon: str, polygon_srid: int):
        """
        counted cells as {population, polygon: [[lat, lng] x 4]},
        None if more than MAX_CELLS
        """
        rows = LocationRepository.get_cells_by_polygon(
            grid, polygon, polygon_srid, cell_size_m(grid.size) / 2, MAX_CELLS + 1
        )
        if len(rows) > MAX_CELLS:
            return None
        return [{"population": people, "polygon": _square(square)} for people, square in rows]

    @staticmethod
    def location_from_csv(
        grid: Grid,
        x_column: str,
        y_column: str,
        population_key: str,
        csv: DataFrame
    ):
        """
        builds location from csv entry
        """
        locations = [
            Location(
                grid_id=grid.id,
                geom=f"SRID={grid.srid};POINT({row[x_column]} {row[y_column]})",
                population=row[population_key]
            ) for _, row in csv.iterrows()
        ]
        number_of_locations = LocationRepository.set_bulk_locations(locations)

        return number_of_locations
