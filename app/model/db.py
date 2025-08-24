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
from typing import Optional, Any
from sqlmodel import Field, SQLModel, UniqueConstraint
from sqlalchemy import Column
from geoalchemy2 import Geometry

from app.model.dto import GridDTO, FullGridDTO


class Grid(SQLModel, table=True):
    """
    class handles model of Grid
    """
    __table_args__ = (
        UniqueConstraint("name", "size", "srid", name="unique_grid"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    size: str
    srid: int

    @classmethod
    def from_dto(cls, dto: GridDTO):
        """
        transforms GridDTO to Grid
        """
        grid = cls(
            name=dto.name,
            size=dto.size,
            srid=dto.srid
        )
        return grid

    def to_dto_with_number(self, number_of_location: int) -> FullGridDTO:
        """Transform into FullGridDTO with an extra field"""
        return FullGridDTO(
            id=self.id,
            name=self.name,
            size=self.size,
            srid=self.srid,
            number_of_location=number_of_location,
        )


class Location(SQLModel, table=True):
    """
    class handles model of Location
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    grid_id: int = Field(default=None, foreign_key="grid.id")
    geom: Any = Field(sa_column=Column(Geometry("POINT"), nullable=False))
    population: int
