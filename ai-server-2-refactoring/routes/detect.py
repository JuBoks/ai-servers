from fastapi import APIRouter, Body, HTTPException

from models.common import Response
from models.detect import UpdateDetectTnrModel
import services.detect_service as detect_service

router = APIRouter(prefix="/detect")


@router.post(
    "/batch",
    summary="[Batch]CPU-Bound Detection (takes about 30sec)",
    response_model=Response,
)
async def batch_result(serial_number: str, date: str):
    # face detection 수행 및 결과 도출
    result = await detect_service.face_detection(serial_number, date)
    if result.status_code == 600:
        raise HTTPException(status_code=500, detail=f"Internal Server Error.")
    elif result.status_code == 601:
        raise HTTPException(
            status_code=500, detail=f"Sending cluster information is failed."
        )

    result.status_code = 200
    return result

@router.get(
    "/tnr",
    summary="분석결과 중 tnr관련 정보만 조회",
    response_model=Response,
)
async def get_tnr_datas(serial_number: str, date: str) -> Response:
    return await detect_service.retrieve_tnr(serial_number, date)

@router.put(
    "/tnr",
    summary="분석결과 중 tnr관련 정보만 수정",
    response_model=Response,
)
async def put_tnr_datas(serial_number: str, date: str, req: UpdateDetectTnrModel = Body(...)) -> Response:
    return await detect_service.update_detect(serial_number, date, req.dict())

@router.put(
    "/undo",
    summary="분석결과를 원본으로 초기화하기",
    response_model=Response,
)
async def put_detect_undo(
    serial_number: str, date: str
) -> Response:
    return await detect_service.update_detect_undo(serial_number, date)



# @router.get(
#     "/", summary="get all results", response_model=Response
# )
# async def get_batch_results():
#     results = await retrieve_detects()
#     return Response(status_code=status.HTTP_200_OK, content=results)
