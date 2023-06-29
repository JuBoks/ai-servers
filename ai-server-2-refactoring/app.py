from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv(os.path.abspath(".env.dev"))

from config.config import initiate_database
from routes.detect import router as DetectRouter


app = FastAPI()
app.mount("/aiapi", app)


@app.on_event("startup")
async def start_database():
    await initiate_database()


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app."}


app.include_router(DetectRouter, tags=["Detects"])
