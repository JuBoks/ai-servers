from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv(os.path.abspath(".env.dev"))

from config.config import initiate_database
from routes.detect import router as DetectRouter
from routes.info import router as InfoRouter
from routes.temp import router as TempRouter


app = FastAPI()
app.mount("/aiapi", app)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # cookie 포함 여부를 설정한다. 기본은 False
    allow_methods=["*"],  # 허용할 method를 설정할 수 있으며, 기본값은 'GET'이다.
    allow_headers=[
        "*"
    ],  # 허용할 http header 목록을 설정할 수 있으며 Content-Type, Accept, Accept-Language, Content-Language은 항상 허용된다.
)

@app.on_event("startup")
async def start_database():
    await initiate_database()


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app."}


app.include_router(DetectRouter, tags=["Detects"])
app.include_router(InfoRouter, tags=["Infos"])
app.include_router(TempRouter, tags=["Temps"])
