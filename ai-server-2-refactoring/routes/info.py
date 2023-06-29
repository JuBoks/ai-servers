from fastapi import APIRouter, Body

from models.common import Response
from models.detect import UpdateDetectModel
import services.detect_service as detect_service

router = APIRouter(prefix="/info")

@router.get(
    "",
    summary="[임시 API] GET /detect와 같이 분석결과 조회",
    response_model=Response,
)
async def get_batch_results(serial_number: str, date: str):
    return await detect_service.retrieve_detect(serial_number, date)

@router.put(
    "",
    summary="[임시 API] PUT /detect와 같이 분석결과 수정",
    response_model=Response,
)
async def put_detect(
    serial_number: str, date: str, req: UpdateDetectModel = Body(...)
):
    return detect_service.update_detect(serial_number, date, req.dict())


@router.get("/status", summary="[임시 API] '날짜': int 형태로 분석결과 status 조회(0: AI가 판별, 1: 유저가 수정, -1: invalid)")
async def get_info_status(serial_number: str):
    return await detect_service.retrieve_status(serial_number)


