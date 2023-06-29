from fastapi import APIRouter, Body, HTTPException, status

from database.detect import *
from models.common import Response
from models.detect import *
from services.detect_service import *
from utils.common import send_cat_tnr_info

router = APIRouter()

BACK_AI_URL = os.environ["BACK_AI_URL"]


@router.post(
    "/detection",
    response_description="[Batch]CPU-Bound Detection (takes about 30sec)",
    response_model=Response,
)
async def batch_result(serial_number: str, date: str):
    # face detection 수행 및 결과 도출
    result = await face_detection(serial_number, date)
    if result["status_code"] == 500:
        # Back서버에 개체 수와 tnr 수 update하기
        isSuccess = send_cat_tnr_info(BACK_AI_URL, serial_number, date, 0, 0)
        raise HTTPException(status_code=500, detail=f"Server Error")

    content = result["content"]
    num_clusters = content["num_clusters"]
    tnr_count = content["tnr_count"]

    result = Detect(**content)
    try:
        new_result = await add_detect(result)

        # Back서버에 개체 수와 tnr 수 update하기
        isSuccess = send_cat_tnr_info(
            BACK_AI_URL,
            serial_number,
            date,
            num_clusters,
            tnr_count,
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Couldn't save result")

    if isSuccess == False:
        raise HTTPException(
            status_code=500, detail=f"Sending cluster information is failed."
        )

    return Response(status_code=status.HTTP_201_CREATED, content=new_result)


@router.get(
    "/info",
    response_description="search result by serial number and date",
    response_model=Response,
)
async def get_batch_results(serial_number: str, date: str):
    results = await retrieve_detect(serial_number, date)
    return Response(status_code=status.HTTP_200_OK, content=results)


@router.put(
    "/info",
    response_description="modify result",
    response_model=Response,
)
async def get_batch_results(
    serial_number: str, date: str, req: UpdateDetectModel = Body(...)
):
    # id 찾기
    detect = await retrieve_detect(serial_number, date)

    if detect is not None:
        updated_detect = await update_detect_data(detect.id, req.dict())
        if updated_detect:
            return Response(status_code=status.HTTP_200_OK, content=updated_detect)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@router.get("/representatives", response_description="대표이미지 조회")
async def get_representatives(serial_number: str):
    # 파일 읽어오기
    json_file = await retrieve_detect_representatives(serial_number)

    # '날짜': [] 형태로 result 만들기
    result = {}
    for el in json_file:
        result[el.date] = el.representative_images

    return result


@router.get("/info/status", response_description="분석 결과 status 조회")
async def get_info_status(serial_number: str):
    # 파일 읽어오기
    json_file = await retrieve_detect_status(serial_number)

    # '날짜': int 형태로 result 만들기
    result = {}
    for el in json_file:
        result[el.date] = el.status

    return result


# @router.get(
#     "/detection", response_description="get all results", response_model=Response
# )
# async def get_batch_results():
#     results = await retrieve_detects()
#     return Response(status_code=status.HTTP_200_OK, content=results)
