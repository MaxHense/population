import os

from sqlmodel import Field, SQLModel, UniqueConstraint, Session, create_engine
from sqlalchemy import Column
from geoalchemy2 import Geometry
from typing import Optional, Any
from app.models import GridDTO
from dotenv import load_dotenv

db_url = os.environ['DBURL']

engine = create_engine(db_url, echo=True)

class Grid(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "size", "definition", name="unique_grid"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    size: str
    definition: str

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
    geom: Any = Field(sa_column=Column(Geometry("POINT", srid=3035)))
    population: int
