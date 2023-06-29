from fastapi import APIRouter

import services.detect_service as detect_service

router = APIRouter()

@router.get("/representatives", summary="📌 냥그릇 대표이미지 조회")
async def get_representatives(serial_number: str):
    # 추후 Response양식에 맞게 보내고 client쪽 수정
    result = await detect_service.retrieve_representatives(serial_number)
    return result.content