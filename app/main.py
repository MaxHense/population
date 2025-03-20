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
- POST /upload/: Accepts a grid definition, a CSV file, and a population key,
    processes the data, and returns the processed grid information.
TODO:
- Implement Alembic for database migrations.
"""
import json

from io import StringIO
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, UploadFile, HTTPException

import pandas as pd

from app.models import GridDTO, FullGridDTO
from app.model import Grid, Location
from app.logger import logger


#TODO: Implement alembic for database migrations
def db_init():
    logger.info("Hallo, Startup")

@asynccontextmanager
async def lifespan(my_app: FastAPI):
    db_init()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/upload/")
async def upload_file(
    grid: str = Form(...),
    file: UploadFile = File(...),
    population_key: str = Form(...),
):
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
