"""Request bodies of the API."""
from pydantic import BaseModel


class PolygonDTO(BaseModel):
    """polygon as WKT in the CRS polygon_srid (the browser sends WGS84, 4326)"""
    polygon_srid: int
    polygon: str
