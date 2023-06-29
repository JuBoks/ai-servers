import os.path
import datetime
from glob import glob
import requests
import json
import shutil

# FastAPI에서 CORSMiddleware라는 모듈로 CORS를 제어한다.
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio

# Google
from google_drive import connect_to_google_drive, upload_photo
from dotenv import load_dotenv

# YOLO
from yolov5.yolo import detectCatByYolo

# s3
from s3upload import upload_image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI(static_directory="static")

app.mount("/fastapi", app)
app.mount("/fastapi/static", StaticFiles(directory="static"), name="static")

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

# Google Drive 서비스
googleService = connect_to_google_drive()

# Spring 서버 URL
SERVER_URL = os.environ["SERVER_URL"]

# 전역 시간
REALTIME = {"iujeong": "", "jeongho": "", "mihyeon": ""}


@app.get("/yolo/pics")
def yolo_pics():
    return display_yolo_pics("static/yolov5/*.png", "Cats Detected By YOLO")


@app.get("/img/pics")
def img_pics():
    return display_pics("static/realtime/*.png", "실시간 사진들")


@app.post("/upload-google/{serial_number}")
async def upload_google_model_yolo_detr(
    serial_number, imageFile: UploadFile or None = None
):
    if not imageFile:
        return {"status": 400, "message": "There is no file"}

    # 이미지 파일인지 식별하기
    contentType, ext = imageFile.content_type.split("/")
    if contentType != "image":
        return {"status": 400, "message": "Not a image file"}

    # 이미지 파일 읽기
    contents = await imageFile.read()

    # 실시간 이미지 파일 이름 설정
    siteId = os.environ[serial_number]
    siteName = os.environ[serial_number + "_NAME"]

    # 구글에 업로드할 구글 파일 이름 설정
    googleFileName = datetime.datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    REALTIME[siteName] = googleFileName
    googleFileName = f"{siteName}_{googleFileName}"

    # 읽은 파일을 보내기 위해 서버에 저장
    realtimeFilePath = f"static/realtime/{siteName}.png"
    inputFilePath = f"static/input/{googleFileName}.png"

    paths = [realtimeFilePath, inputFilePath]
    for path in paths:
        with open(path, "wb") as f:
            f.write(contents)

    # status = await filterCatByYolo(inputFilePath, googleFileName)
    status = True

    if status:
        # 파일 포인터를 파일의 처음으로 옮겨줍니다.
        await imageFile.seek(0)

        # 구글에 사진 전송, S3로 파일 업로드 및 객체 정보 저장
        # tasks = [
        #     asyncio.create_task(
        #         # upload_photo(googleService, inputFilePath, googleFileName, siteId),
        #         asyncio.create_task(upload_s3(serial_number, imageFile))
        #     )
        # ]

        # results = await asyncio.gather(*tasks)
        result = upload_s3(serial_number, imageFile)

        if result:
            # if results[0]:  # and results[1]:
            return {
                "status": 200,
                "message": "cat detection and upload images are successful.",
            }
        else:
            return {"status": 500, "message": "Image Uploading is failed."}
    else:
        return {"status": 200, "message": "No Cat."}


# @app.post("/upload-s3/{serial_number}")
def upload_s3(serial_number, imageFile: UploadFile or None = None):
    try:
        imagePath = upload_image(serial_number, imageFile)
    except Exception as e:
        print("이미지 업로드 도중 에러 발생", e)
        return {"status": 500, "message": "이미지 업로드 도중 에러 발생"}

    # back에 정보 보내기
    # POST 요청을 보낼 URL
    url = f"{SERVER_URL}/ai/image"

    # POST 요청에 포함할 데이터
    data = {
        "dishSerialNum": serial_number,
        "imagePath": imagePath,
    }

    # 요청 본문에 포함할 데이터를 JSON 형식으로 인코딩
    json_data = json.dumps(data)

    # 요청 본문과 함께 POST 요청 보내기
    response = requests.post(
        url, data=json_data, headers={"Content-Type": "application/json"}
    )

    # print(response.text)
    # 응답 결과 출력
    if response.status_code >= 400:
        return False
    else:
        return True


def display_pics(filePath, title):
    image_list = glob(filePath)

    html_content = f"<html><body><h3>{title}</h3><div style='display: flex; gap: 10px; flex-wrap: wrap;'>"
    for image in image_list:
        dirpath, filename = os.path.split(image)
        filename = filename.split(".")[0]
        html_content += f'<div><div>{filename}_{REALTIME[filename]}</div><img src="/fastapi/{image}" alt="{filename}" width="416" ></div>'
    html_content += "</div></body></html>"

    return HTMLResponse(content=html_content, status_code=200)


def display_yolo_pics(filePath, title):
    image_list = glob(filePath)

    html_content = f"<html><body><h3>{title}</h3><div style='display: flex; gap: 10px; flex-wrap: wrap;'>"
    for image in image_list:
        dirpath, filename = os.path.split(image)
        filename = filename.split(".")[0]
        html_content += f'<div><div>{filename}</div><img src="/fastapi/{image}" alt="{filename}" width="416" ></div>'
    html_content += "</div></body></html>"

    return HTMLResponse(content=html_content, status_code=200)


async def filterCatByYolo(inputFilePath, googleFileName):
    # 1. 이미지 파일을 yolo로 고양이 사진 필터링
    isCat = await detectCatByYolo(inputFilePath)
    if isCat:
        # yolo로 통과된 사진을 보여주기 위해 yolo폴더에 저장
        yoloFilePath = f"static/yolov5/{googleFileName}.png"
        shutil.copyfile(inputFilePath, yoloFilePath)

    return isCat
