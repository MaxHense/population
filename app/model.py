import os

from sqlmodel import Field, SQLModel, UniqueConstraint, Session, create_engine
from sqlalchemy import Column
from geoalchemy2 import Geometry
from typing import Optional, Any
from app.models import GridDTO, FullGridDTO
from dotenv import load_dotenv
from pandas import DataFrame
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

db_url = os.environ['DBURL']

engine = create_engine(db_url, echo=False)

class Grid(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "size", "definition", name="unique_grid"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    size: str
    definition: str

    #TODO: Integrity Error catch
    @classmethod
    def from_dto(cls, dto: GridDTO):
        grid = cls(
            name=dto.name,
            size=dto.size,
            definition=dto.definition
        )
        with Session(engine) as session:
            session.add(grid)
            session.commit()
            session.refresh(grid)
            return grid

class Location(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    grid_id: int = Field(default=None, foreign_key="grid.id")
    geom: Any = Field(sa_column=Column(Geometry("POINT", srid=3035), nullable=False))
    population: int

    @classmethod
    def from_csv(cls, grid_id: int, size: str, population_key: str, csv: DataFrame):
        get_x = "x_mp_" + size
        get_y = "y_mp_" + size
        locations = [
            cls(
                grid_id=grid_id,
                geom=f"POINT({row[get_x]} {row[get_y]})",
                population=row[population_key]
            )
            for _, row in csv.iterrows()
        ]
        with Session(engine) as session:
            session.bulk_save_objects(locations)
            session.commit()
