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
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from alembic.config import Config
from alembic import command

import pandas as pd

from app.models import GridDTO, FullGridDTO, PolygonDTO
from app.model import Grid, Location
from app.logger import logger


@asynccontextmanager
async def lifespan(my_app: FastAPI):
    try:
        subprocess.check_call(["alembic", "upgrade", "head"])
        logger.info("Migrations run successfully")
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to run migrations, because of %s", exc, exc_info=True)
        raise RuntimeError("Database migration failed. Shutting down server.")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def get_polygon(polygon: PolygonDTO):
    '''Takes a polygon DTO and returns the population within the polygon'''
    grid = Grid.get_by_id(polygon.grid_id)
    if not grid:
        raise HTTPException(status_code=404, detail="Grid not found")
    poulation = Location.get_by_polygon(grid.id, polygon.polygon)
    print(poulation)
    return {"Bevölkerung": poulation}

@app.post("/upload/")
async def upload_file(
    grid: str = Form(...),
    file: UploadFile = File(...),
    population_key: str = Form(...),
):
    '''Takes a grid definition, a CSV file, and a population key,
        processes the data, and returns the processed grid information'''
    try:
        grid_data = json.loads(grid)
        grid_model = GridDTO(**grid_data)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON for 'grid'") from exc

    new_grid = Grid.from_dto(grid_model)

    new_dto = FullGridDTO.from_model(new_grid)

    contents = await file.read()
    file_content = contents.decode("utf-8")
    df = pd.read_csv(StringIO(file_content), delimiter=";")

    Location.from_csv(new_grid.id, new_grid.size, population_key,  df)

    return {
        "filename": file.filename,
        "grid": new_dto
    }
