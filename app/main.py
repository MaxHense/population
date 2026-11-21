"""
FastAPI app: population inside a polygon.

Stateless, read only. All configuration comes from environment variables:
- DBURL: PostGIS connection URL (required)
- CORS_ORIGINS: comma separated origins allowed to call the API from a browser (optional)

Migrations are not run here; the container entrypoint runs `alembic upgrade head`.
Data is loaded by import scripts (e.g. `python -m scripts.eurostat`), not through the API.

Endpoint:
- POST /: population inside a polygon over all grids, plus the counted cells (None if too many)
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.dto import PolygonDTO
from app.services.location import LocationService

app = FastAPI(title="population counter")

cors_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["POST"],
        allow_headers=["Content-Type"],
    )


@app.post("/")
def get_polygon(polygon: PolygonDTO):
    '''Population within the polygon, summed over all grids'''
    population = LocationService.get_population_by_polygon(polygon.polygon, polygon.polygon_srid)
    cells = LocationService.get_cells_by_polygon(polygon.polygon, polygon.polygon_srid)
    return {"population": population, "cells": cells}
