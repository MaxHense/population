"""
This module defines the database models and their associated methods for the population application.

Classes:
    Grid(SQLModel): Represents a grid entity with attributes such as name, size, and srid.
        - from_dto(cls, dto: GridDTO): Class method to create a Grid instance from a GridDTO
          object and save it to the database.

    Location(SQLModel): Represents a location entity with attributes such as grid_id, geometry,
    and population.
        - from_csv(cls, grid_id: int, size: str, population_key: str, csv: DataFrame): 
          Class method to create multiple Location instances from a CSV DataFrame and
          save them to the database.

Modules:
    - sqlmodel: Provides the base class and utilities for defining SQLAlchemy models.
    - geoalchemy2: Provides support for spatial data types and operations.
    - pandas: Used for handling CSV data as DataFrame.
    - dotenv: Used for loading environment variables.
    - logging: Configures logging for the application.

Constants:
    - db_url (str): The database connection URL loaded from environment variables.
    - engine: The SQLAlchemy engine instance for database operations.

Notes:
    - The `Grid` class includes a unique constraint on the combination of
      name, size, and srid.
    - The `Location` class uses the GeoAlchemy2 `Geometry` type for spatial data.
    - Logging is configured to suppress detailed SQLAlchemy engine logs by default.
"""
import os

from typing import Optional, Any
from sqlmodel import Field, SQLModel, UniqueConstraint, select
from sqlalchemy import Column, func
from geoalchemy2 import Geometry
from dotenv import load_dotenv
from pandas import DataFrame

from app.models import GridDTO
from app.db import get_engine, get_session

class Grid(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "size", "srid", name="unique_grid"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    size: str
    srid: int

    #TODO: Integrity Error catch
    @classmethod
    def from_dto(cls, dto: GridDTO):
        grid = cls(
            name=dto.name,
            size=dto.size,
            srid=dto.srid
        )
        with get_session() as session:
            session.add(grid)
            session.commit()
            session.refresh(grid)
            return grid

    @classmethod
    def get_by_id(cls, grid_id: int):
        with get_session() as session:
            return session.get(cls, grid_id)

class Location(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    grid_id: int = Field(default=None, foreign_key="grid.id")
    geom: Any = Field(sa_column=Column(Geometry("POINT"), nullable=False))
    population: int

    @classmethod
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
        with get_session() as session:
            session.bulk_save_objects(locations)
            session.commit()

    @classmethod
    def get_by_polygon(cls, grid: Grid, polygon: str, polygon_srid: int):
        with get_session() as session:
            statement = select(func.sum(cls.population)).where(cls.grid_id == grid.id).where(
                func.ST_Contains(
                    func.ST_Transform(
                        func.ST_SetSRID(
                            func.ST_GeomFromText(polygon), polygon_srid
                        ),
                        grid.srid
                    ),
                    cls.geom
                )
            )
            return session.exec(statement).first()
