import os
import requests
from utils.common import *
from .face_detection import detection
from .image_clustering import cluster_images
from .tnr_filtering import detect_tnr


FILE_SAVE_PATH = os.path.abspath("datasets/0_files")

BACK_URL = os.environ["BACK_URL"]
BACK_AI_URL = os.environ["BACK_AI_URL"]


def get_files(serial_number, date, file_path):
    # 폴더 비우기
    empty_directory(f"{file_path}/*")

    # 사진 파일 가져오기
    url = "/ai/image"
    params = {"date": date, "dishSerialNum": serial_number}
    response = requests.get(BACK_URL + url, params=params)
    # 응답 처리
    if response.status_code != 200:
        return {"status": 500, "message": "get files failed."}

    result = response.json()  # JSON 응답 데이터 파싱

    os.makedirs(file_path, exist_ok=True)

    img_info = {}
    for el in result["data"]:
        path = el["imagePath"]
        id = el["dishImageId"]
        save_image_from_url(path, f"{file_path}/{id}.jpg")
        img_info[f"{id}.jpg"] = path

    return img_info


async def face_detection(serial_number, date):
    status_code = 500

    try:
        # 시리얼번호에 따른 경로 찾기
        folder_name = os.environ[f"{serial_number}"]
        file_path = os.path.abspath(f"{FILE_SAVE_PATH}/{folder_name}")

        # 1. back으로부터 사진 파일 다운로드 하기
        img_info = get_files(serial_number, date, file_path)

        # 2. 다운로드 받은 사진들에 대해서 detection 진행하기
        # detection(file_path)

        # 3. cluster 진행
        result = cluster_images(serial_number)

        # 4. tnr판별
        result_tnr, tnrCount = detect_tnr()

        # 5. 데이터 정제
        for el in result["representative_images"]:
            el[1] = img_info[el[1]]
        for el in result["file_feature_info"]:
            el[0] = img_info[el[0]]
        for images in result["closest_images"]:
            for i in range(len(images)):
                images[i] = img_info[images[i]]
        result["tnr_info"] = []
        for el in result_tnr:
            result["tnr_info"].append([img_info[el[0]], el[1]])
        result["tnr_count"] = tnrCount
        result["serial_number"] = serial_number
        result["date"] = date

        status_code = 200

    except:
        result = {"status": -1, "serial_number": serial_number, "date": date}

    return {"status_code": status_code, "content": result}
