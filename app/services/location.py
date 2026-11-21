"""
module holds the service for locations
"""
import json

from app.repositories.location import LocationRepository


MAX_CELLS = 2000  # more cells are not sent to the browser, the total is still returned


def _square(geojson: str) -> list[list[float]]:
    ring = json.loads(geojson)["coordinates"][0][:-1]
    return [[lat, lng] for lng, lat in ring]


class LocationService:
    """
    this class is the service for locations
    """
    @staticmethod
    def get_population_by_polygon(polygon: str, polygon_srid: int):
        """
        returns population of specified polygon, over all grids
        """
        return LocationRepository.get_population_by_polygon(polygon, polygon_srid)

    @staticmethod
    def get_cells_by_polygon(polygon: str, polygon_srid: int):
        """
        counted cells of all grids as {population, polygon: [[lat, lng] x 4]},
        None if more than MAX_CELLS
        """
        rows = LocationRepository.get_cells_by_polygon(polygon, polygon_srid, MAX_CELLS + 1)
        if len(rows) > MAX_CELLS:
            return None
        return [{"population": people, "polygon": _square(square)} for people, square in rows]
