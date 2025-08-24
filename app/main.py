"""
This module defines the main application logic for a FastAPI-based service
that processes grid data and population information.
The application provides an endpoint to upload a grid definition and a CSV
file containing population data. The uploaded data is validated, processed,
and stored in the application's data model.
Modules and Libraries:
- pandas: Used for processing CSV data.
- json: Used for parsing and validating JSON input.
- contextlib: Provides utilities for managing application lifespan.
- fastapi: Framework for building the web application.
- io: Used for handling in-memory file operations.
- app.models: Contains data transfer object (DTO) definitions.
- app.model: Contains core application models.
- app.logger: Provides logging functionality.
Endpoints:
- GET /: Accepts a grid ID and a polygon definition, retrieves the population
- POST /upload/: Accepts a grid definition, a CSV file, and a population key,
    processes the data, and returns the processed grid information.
"""
import json
import subprocess

from io import StringIO
from typing import Callable
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request, Response
from fastapi.routing import APIRoute

import pandas as pd

from app.model.dto import GridDTO, PolygonDTO, DataDTO
from app.model.db import Grid
from app.log import logger
from app.services.grid import GridService
from app.services.location import LocationService


class LogRequestResponse(APIRoute):
    """
    Handles that response of app gets logged
    """
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            req = await request.body()
            logger.info("Request: %s", req)
            response: Response = await original_route_handler(request)
            logger.info("Response: %s", response.body)
            return response

        return custom_route_handler


@asynccontextmanager
async def lifespan(my_app: FastAPI):
    """
    Checks if alembic has successfully upgraded the database
    """
    try:
        subprocess.check_call(["alembic", "upgrade", "head"])
        logger.info("Migrations run successfully for app: %s", my_app.title)
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to run migrations, because of %s", exc, exc_info=True)
        raise RuntimeError("Database migration failed. Shutting down server.") from exc
    yield

app = FastAPI(title="population counter", lifespan=lifespan)
app.router.route_class = LogRequestResponse


@app.get("/")
async def get_polygon(polygon: PolygonDTO):
    '''Takes a polygon DTO and returns the population within the polygon'''
    grid = GridService.get_by_id(polygon.grid_id)
    if not grid:
        raise HTTPException(status_code=404, detail="Grid not found")
    poulation = LocationService.get_population_by_polygon(
        grid,
        polygon.polygon,
        polygon.polygon_srid
    )
    print(poulation)
    return {"Bevölkerung": poulation}


@app.post("/upload/")
async def upload_file(
    grid: str = Form(...),
    file: UploadFile = File(...),
    data_definition: str = Form()
):
    '''Takes a grid definition, a CSV file, and a population key,
        processes the data, and returns the processed grid information'''
    try:
        grid_data = json.loads(grid)
        grid_model = GridDTO(**grid_data)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON for 'grid'"
        ) from exc

    try:
        data_definition = json.loads(data_definition)
        data_model = DataDTO(**data_definition)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON for 'grid'"
        ) from exc

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


@app.post("/grid")
def add_grid(grid: GridDTO):
    '''Takes a grid DTO and adds it to the database'''
    new_grid = Grid.from_dto(grid)
    return new_grid
