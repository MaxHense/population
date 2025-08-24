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
                geom = f"SRID={grid.srid};POINT({row[x_column]} {row[y_column]})",
                population=row[population_key]
            )
            for _, row in csv.iterrows()
        ]
        number_of_locations = LocationRepository.set_bulk_locations(locations)

        return number_of_locations
