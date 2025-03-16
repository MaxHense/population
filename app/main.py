import pandas as pd
import logging
import subprocess
import sys

from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI, UploadFile
from io import StringIO
from starlette.background import BackgroundTasks

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set logging level to INFO
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def db_init():
    logger.info("Hallo, Startup")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_init()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/upload/")
async def upload_file(file: UploadFile):
    contents = await file.read()
    file_content = contents.decode("utf-8")
    df = pd.read_csv(StringIO(file_content))
    return {"filename": file.filename}
