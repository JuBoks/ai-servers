import os
from fastapi import HTTPException, status

from .image_clustering import cluster_images
from .tnr_filtering import detect_tnr
from utils.common import send_cat_tnr_info, get_files
# models
from models.common import Response
from models.detect import Detect
from models.original import Original
# dao
import database.detect as detect_dao
import database.original as original_dao

FILE_SAVE_PATH = os.path.abspath("datasets/0_files")

BACK_URL = os.environ["BACK_URL"]
BACK_AI_URL = os.environ["BACK_AI_URL"]

async def retrieve_detect(serial_number: str, date: str) -> Response:
    results = await detect_dao.retrieve_detect(serial_number, date)
    return Response(status_code=status.HTTP_200_OK, content=results)

async def retrieve_tnr(serial_number: str, date: str) -> Response:
    result = await detect_dao.retrieve_detect_tnr(serial_number, date)
    return Response(status_code=status.HTTP_200_OK, content=result)

async def retrieve_status(serial_number: str) -> Response:
    json_file = await detect_dao.retrieve_detect_status(serial_number)

    # '날짜': int 형태로 result 만들기
    result = {}
    for el in json_file:
        result[el.date] = el.status

    return Response(status_code=status.HTTP_200_OK, content=result)

async def retrieve_representatives(serial_number: str) -> Response:
    json_file = await detect_dao.retrieve_detect_representatives(serial_number)

    # '날짜': [] 형태로 result 만들기
    result = {}
    for el in json_file:
        result[el.date] = el.representative_images

    return Response(status_code=status.HTTP_200_OK, content=result)

async def face_detection(serial_number: str, date: str) -> Response:
    result = Response()

    try:
        # 시리얼번호에 따른 경로 찾기
        folder_name = os.environ[f"{serial_number}"]
        file_path = os.path.abspath(f"{FILE_SAVE_PATH}/{folder_name}")

        # 1. back으로부터 사진 파일 다운로드 하기
        img_info = get_files(serial_number, date, file_path)

        # 2. 다운로드 받은 사진들에 대해서 detection 진행하기
        # detection(file_path)

        # 3. cluster 진행
        content = cluster_images(serial_number)

        # 4. tnr판별
        content_tnr, tnrCount = detect_tnr()

        # 5. 데이터 정제
        for el in content["representative_images"]:
            el[1] = img_info[el[1]]
        for el in content["file_feature_info"]:
            el[0] = img_info[el[0]]
        for images in content["closest_images"]:
            for i in range(len(images)):
                images[i] = img_info[images[i]]
        content["tnr_info"] = []
        for el in content_tnr:
            content["tnr_info"].append([img_info[el[0]], el[1]])
        content["tnr_count"] = tnrCount
        content["serial_number"] = serial_number
        content["date"] = date

        # 6. mongoDB에 저장
        content_detect = Detect(**content)
        new_content = await detect_dao.add_detect(content_detect)
        content_original = Original(**content)
        await original_dao.add_original(content_original)

        # 7. Back서버에 개체 수와 tnr 수 update하기
        isSuccess = send_cat_tnr_info(serial_number, date, content_detect.num_clusters, content_detect.tnr_count)

        if isSuccess == False:
            result.status_code = 601
            return result

        # 8. 성공
        result.content = new_content
        result.status_code = 200

    except Exception as e:
        result.status_code = 600

    return result

async def update_detect(serial_number: str, date: str, data: dict):
    # id 찾기
    detect = await detect_dao.retrieve_detect(serial_number, date)
    if detect is None:
        raise HTTPException(status_code=404, detail=f"Detect is not found")
    
    # 업데이트 하기
    updated_detect = await detect_dao.update_detect(detect.id, data)
    if updated_detect is None:
        raise HTTPException(status_code=500, detail=f"Updating Detect is failed")

    # Back서버에 tnr관련 update하기
    send_cat_tnr_info(serial_number, date, detect.num_clusters, detect.tnr_count)

    return Response(status_code=status.HTTP_200_OK, content=updated_detect)


async def update_detect_undo(serial_number: str, date: str):
    # 원본찾기
    original = await original_dao.retrieve_original(serial_number, date)

    if original is None:
        raise HTTPException(status_code=404, detail=f"Original is not found")
    
    return await update_detect(serial_number, date, original.dict())
