"""
FastAPI app: population inside a polygon.

Stateless. All configuration comes from environment variables:
- DBURL: PostGIS connection URL (required)
- ADMIN_TOKEN: enables admin endpoints, sent as bearer token (optional)
- CORS_ORIGINS: comma separated origins allowed to call the API from a browser (optional)

Migrations are not run here; the container entrypoint runs `alembic upgrade head`.

Endpoints:
- POST /: population inside a polygon, plus the counted cells (None if too many)
- GET /grid: all grids
- POST /admin/grids: (needs ADMIN_TOKEN) upload a grid definition and a CSV with population
"""
import os
import secrets
from io import StringIO

import pandas as pd
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ValidationError

from app.models.dto import DataDTO, GridDTO, PolygonDTO
from app.services.grid import GridService
from app.services.location import LocationService

app = FastAPI(title="population counter")

cors_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )

_bearer = HTTPBearer(auto_error=False)


def require_admin(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)):
    """Admin endpoints exist only if ADMIN_TOKEN is set,
    then a matching bearer token is required."""
    token = os.environ.get("ADMIN_TOKEN")
    if not token:
        raise HTTPException(status_code=404)
    given = credentials.credentials.encode() if credentials else b""
    if not secrets.compare_digest(given, token.encode()):
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Bearer"})


def parse_form_json[T: BaseModel](model: type[T], field: str, value: str) -> T:
    """Parse a JSON form field into a model, 400 on invalid JSON or missing fields."""
    try:
        return model.model_validate_json(value)
    except ValidationError as exc:
        detail = f"Invalid '{field}': {exc.errors()[0]['msg']}"
        raise HTTPException(status_code=400, detail=detail) from exc


@app.post("/")
async def get_polygon(polygon: PolygonDTO):
    '''Takes a polygon DTO and returns the population within the polygon'''
    grid = GridService.get_by_id(polygon.grid_id)
    if not grid:
        raise HTTPException(status_code=404, detail="Grid not found")
    population = LocationService.get_population_by_polygon(
        grid,
        polygon.polygon,
        polygon.polygon_srid
    )
    cells = LocationService.get_cells_by_polygon(grid, polygon.polygon, polygon.polygon_srid)
    return {"population": population, "cells": cells}


@app.post("/admin/grids", dependencies=[Depends(require_admin)])
async def upload_file(
    grid: str = Form(...),
    file: UploadFile = File(...),
    data_definition: str = Form()
):
    '''Takes a grid definition, a CSV file, and a population key,
        processes the data, and returns the processed grid information'''
    grid_model = parse_form_json(GridDTO, "grid", grid)
    data_model = parse_form_json(DataDTO, "data_definition", data_definition)

    new_grid = GridService.set_new_grid(grid_model)

    contents = await file.read()
    file_content = contents.decode(data_model.decode)
    df = pd.read_csv(StringIO(file_content), delimiter=data_model.delimiter)

    number_of_location = LocationService.location_from_csv(
        new_grid,
        data_model.x_column,
        data_model.y_column,
        data_model.population_key,
        df
    )

    return new_grid.to_dto_with_number(number_of_location)


@app.get("/grid")
def get_grid():
    '''Returns all Grids of database'''
    return GridService.list_grids()
