"""
Database tables.

- Grid: one dataset of cells (e.g. Eurostat Census 2021): name, cell size in metres,
  CRS of its source data (srid).
- Location: centre of one cell with its population, always in EPSG:3035 (STORAGE_SRID),
  whatever the CRS of the source data. So one query covers all grids.

Data is loaded by import scripts (scripts/, e.g. scripts.eurostat), not through the API.
"""
from typing import Optional, Any
from sqlmodel import Field, SQLModel, UniqueConstraint
from sqlalchemy import Column
from geoalchemy2 import Geometry

# ponytail: one CRS for all cells, equal-area for Europe;
# data outside Europe needs another CRS (or geography)
STORAGE_SRID = 3035


class Grid(SQLModel, table=True):
    """one dataset of cells"""
    __table_args__ = (
        UniqueConstraint("name", name="unique_grid_name"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    cell_size_m: int
    srid: int  # CRS of the source data, cells are stored in STORAGE_SRID


class Location(SQLModel, table=True):
    """centre of one cell with its population"""
    id: Optional[int] = Field(default=None, primary_key=True)
    grid_id: int = Field(default=None, foreign_key="grid.id")
    geom: Any = Field(sa_column=Column(Geometry("POINT", srid=STORAGE_SRID), nullable=False))
    population: int
