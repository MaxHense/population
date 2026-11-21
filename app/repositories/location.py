"""
module is the repository for location
"""
from sqlmodel import select
from sqlalchemy import func

from app.models.db import Location, Grid, STORAGE_SRID
from app.repositories.db import get_session


def _inside(polygon: str, polygon_srid: int):
    """a cell of any grid counts if its centre is inside the polygon"""
    drawn = func.ST_SetSRID(func.ST_GeomFromText(polygon), polygon_srid)
    return func.ST_Contains(func.ST_Transform(drawn, STORAGE_SRID), Location.geom)


class LocationRepository:
    """
    class handles all database requests for locations
    """
    @staticmethod
    def get_population_by_polygon(polygon: str, polygon_srid: int):
        """
        return population of specified polygon
        """
        with get_session() as session:
            statement = select(func.sum(Location.population)).where(
                _inside(polygon, polygon_srid)
            )
            return session.exec(statement).first()

    @staticmethod
    def get_cells_by_polygon(polygon: str, polygon_srid: int, limit: int):
        """
        return (population, GeoJSON square in WGS84) of every counted cell,
        each in the size of its grid, at most limit rows
        """
        cell = func.ST_Expand(Location.geom, Grid.cell_size_m / 2.0)
        square = func.ST_AsGeoJSON(func.ST_Transform(cell, 4326))
        with get_session() as session:
            statement = select(Location.population, square).join(Grid).where(
                _inside(polygon, polygon_srid)
            ).limit(limit)
            return session.exec(statement).all()
