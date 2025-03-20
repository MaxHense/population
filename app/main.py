import pandas as pd
import json

from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from io import StringIO
from app.models import GridDTO, FullGridDTO 
from app.model import Grid, Location
from app.logger import logger

#TODO: Implement alembic for database migrations
def db_init():
    logger.info("Hallo, Startup")

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for 'grid'")
    
    newGrid = Grid.from_dto(grid_model)

    newDTO = FullGridDTO.from_model(newGrid)

    contents = await file.read()
    file_content = contents.decode("utf-8")
    df = pd.read_csv(StringIO(file_content), delimiter=";")

    Location.from_csv(newGrid.id, newGrid.size, population_key,  df)

    return {
        "filename": file.filename,
        "grid": newDTO
    }
