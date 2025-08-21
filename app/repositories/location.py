from sqlmodel import select
from sqlalchemy import Column, func
from app.model import Location, Grid
from app.db import get_session

class LocationRepository:
    @classmethod
    def get_population_by_polygon(cls, grid: Grid, polygon: str, polygon_srid: int):
        with get_session() as session:
            statement = select(func.sum(Location.population)).where(Location.grid_id == grid.id).where(
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
        
    @classmethod
    def set_bulk_locations(cls, locations: list()):
        with get_session() as session:
            session.bulk_save_objects(locations)
            session.commit()
