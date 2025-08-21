"""
This class is the service for locations
"""
from app.repositories.location import LocationRepository
from pandas import DataFrame
from app.model import Grid

class LocationService:
    @staticmethod
    def get_population_by_polygon(grid: Grid, polygon: str, polygon_srid: int):
        return LocationRepository.get_population_by_polygon(grid, polygon, polygon_srid)

    @staticmethod
    def from_csv(cls, grid: Grid, population_key: str, csv: DataFrame):
        get_x = "x_mp_" + grid.size
        get_y = "y_mp_" + grid.size
        locations = [
            cls(
                grid_id=grid.id,
                geom = f"SRID={grid.srid};POINT({row[get_x]} {row[get_y]})",
                population=row[population_key]
            )
            for _, row in csv.iterrows()
        ]
        LocationRepository.set_bulk_locations(locations)
