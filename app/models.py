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
    """
    transfer objet for Grid
    """
    name: str
    size: str
    srid: int

class FullGridDTO(GridDTO):
    """
    transfer objet for returning a Grid
    """
    id: int
    number_of_location: int

class PolygonDTO(BaseModel):
    """
    transfer object of an polygon
    """
    grid_id: int
    polygon_srid: int
    polygon: str
