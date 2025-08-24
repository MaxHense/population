"""
module is the repository for location
"""
from sqlmodel import select
from sqlalchemy import func

from app.models.db import Location, Grid
from app.repositories.db import get_session


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
            statement = select(
                func.sum(Location.population)
            ).where(Location.grid_id == grid.id).where(
                func.ST_Contains(
                    func.ST_Transform(
                        func.ST_SetSRID(
                            func.ST_GeomFromText(polygon), polygon_srid
                        ),
                        grid.srid
                    ),
                    Location.geom
                )
            )
            return session.exec(statement).first()

    @staticmethod
    def set_bulk_locations(locations: []):
        """
        inserts locations in database in bulks
        """
        with get_session() as session:
            session.bulk_save_objects(locations)
            session.commit()
            return len(locations)
