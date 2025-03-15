import pandas as pd

from typing import Union
from fastapi import FastAPI, UploadFile
from io import StringIO
from starlette.background import BackgroundTasks

app = FastAPI()


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

def db_init():
    print("Hello, Startup")

@app.on_event("startup")
async def startup_event():
    db_init