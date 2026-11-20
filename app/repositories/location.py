"""
module is the repository for location
"""
from sqlmodel import select
from sqlalchemy import func

from app.models.db import Location, Grid
from app.repositories.db import get_session


def _inside(grid: Grid, polygon: str, polygon_srid: int):
    """a cell counts if its centre is inside the polygon"""
    drawn = func.ST_SetSRID(func.ST_GeomFromText(polygon), polygon_srid)
    area = func.ST_Transform(drawn, grid.srid)
    return (Location.grid_id == grid.id) & func.ST_Contains(area, Location.geom)


class LocationRepository:
    """
    class handles all database requests for locations
    """
    @staticmethod
    def get_population_by_polygon(grid: Grid, polygon: str, polygon_srid: int):
        """
        return population of specified polygon
        """
        with get_session() as session:
            statement = select(func.sum(Location.population)).where(
                _inside(grid, polygon, polygon_srid)
            )
            return session.exec(statement).first()

    @staticmethod
    def get_cells_by_polygon(
        grid: Grid, polygon: str, polygon_srid: int, half_size: float, limit: int
    ):
        """
        return (population, GeoJSON square in WGS84) of every counted cell,
        at most limit rows
        """
        cell = func.ST_Expand(Location.geom, half_size)
        square = func.ST_AsGeoJSON(func.ST_Transform(cell, 4326))
        with get_session() as session:
            statement = select(Location.population, square).where(
                _inside(grid, polygon, polygon_srid)
            ).limit(limit)
            return session.exec(statement).all()

    @staticmethod
    def set_bulk_locations(locations: []):
        """
        inserts locations in database in bulks
        """
        with get_session() as session:
            session.bulk_save_objects(locations)
            session.commit()
            return len(locations)
