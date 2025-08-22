"""
module holds the service for locations
"""
from pandas import DataFrame

from app.repositories.location import LocationRepository
from app.model import Grid, Location

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
    def from_csv(grid: Grid, population_key: str, csv: DataFrame):
        """
        builds locations from specified csv and stores it in database
        """
        get_x = "x_mp_" + grid.size
        get_y = "y_mp_" + grid.size
        locations = [
            Location(
                grid_id=grid.id,
                geom = f"SRID={grid.srid};POINT({row[get_x]} {row[get_y]})",
                population=row[population_key]
            )
            for _, row in csv.iterrows()
        ]
        LocationRepository.set_bulk_locations(locations)
