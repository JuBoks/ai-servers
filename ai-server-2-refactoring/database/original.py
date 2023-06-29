from typing import List, Union
from beanie import PydanticObjectId
from models.original import Original

async def retrieve_originals() -> List[Original]:
    originals = await Original.all().to_list()
    return originals


async def add_original(new_original: Original) -> Original:
    original = await new_original.create()
    return original


async def retrieve_original(serial_number: str, date: str) -> Original:
    original = await Original.find_one(
        Original.serial_number == serial_number, Original.date == date
    )
    if original:
        return original

async def delete_original(id: PydanticObjectId) -> bool:
    original = await Original.get(id)
    if original:
        await original.delete()
        return True


async def update_original_data(id: PydanticObjectId, data: dict) -> Union[bool, Original]:
    des_body = {k: v for k, v in data.items() if v is not None}
    update_query = {"$set": {field: value for field, value in des_body.items()}}
    original = await Original.get(id)
    if original:
        await original.update(update_query)
        return original
    return False
