from typing import List, Union
from beanie import PydanticObjectId
from models.detect import Detect
from view.detect import DetectRepresentativeView, DetectStatusView, DetectTnrView


async def retrieve_detects() -> List[Detect]:
    detects = await Detect.all().to_list()
    return detects


async def add_detect(new_detect: Detect) -> Detect:
    detect = await new_detect.create()
    return detect


async def retrieve_detect(serial_number: str, date: str) -> Detect:
    detect = await Detect.find_one(
        Detect.serial_number == serial_number, Detect.date == date
    )
    if detect:
        return detect


async def retrieve_detect_representatives(serial_number: str) -> List[DetectRepresentativeView]:
    detect = (
        await Detect.find(Detect.serial_number == serial_number)
        .project(DetectRepresentativeView)
        .to_list()
    )
    return detect


async def retrieve_detect_status(serial_number: str) -> List[DetectStatusView]:
    detect = (
        await Detect.find(Detect.serial_number == serial_number)
        .project(DetectStatusView)
        .to_list()
    )
    return detect

async def retrieve_detect_tnr(serial_number: str, date: str) -> DetectTnrView:
    detect = (
        await Detect.find_one(Detect.serial_number == serial_number, Detect.date == date)
        .project(DetectTnrView)
    )
    return detect


async def delete_detect(id: PydanticObjectId) -> bool:
    detect = await Detect.get(id)
    if detect:
        await detect.delete()
        return True


async def update_detect(id: PydanticObjectId, data: dict) -> Union[None, Detect]:
    des_body = {k: v for k, v in data.items() if v is not None}
    update_query = {"$set": {field: value for field, value in des_body.items()}}
    detect = await Detect.get(id)
    if detect:
        await detect.update(update_query)
        return detect
