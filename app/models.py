"""
This module defines data transfer objects (DTOs) for grid-related data using Pydantic models.

Classes:
    GridDTO: A base DTO representing a grid with attributes for name, size, and definition.
    FullGridDTO: An extended DTO that includes an ID attribute and provides a method to create
                 an instance from a model object.

Methods:
    FullGridDTO.from_model(cls, model): Class method to create a FullGridDTO instance from a
                                        given model object by mapping its attributes.
"""
from pydantic import BaseModel

class GridDTO(BaseModel):
    name: str
    size: str
    srid: int

class FullGridDTO(GridDTO):
    id: int

    @classmethod
    def from_model(cls, model):
        return cls(
            id=model.id,
            name=model.name,
            size=model.size,
            srid=model.srid,
        )

class PolygonDTO(BaseModel):
    grid_id: int
    polygon_srid: int
    polygon: str
