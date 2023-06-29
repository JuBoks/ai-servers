from typing import List
from bson import ObjectId
from beanie import Document
from pydantic import Field, BaseModel
from typing import Optional, Any


class Detect(Document):
    status: int = Field(...)
    serial_number: str = Field(...)
    date: str = Field(...)
    num_clusters: int
    representative_images: List
    width: float
    height: float
    file_feature_info: List
    closest_images: List
    tnr_info: List
    tnr_count: int

    class Settings:
        name = "detections"

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "status": 0,
                "serial_number": "testSerialNumber",
                "date": "2023-05-16",
                "num_clusters": 3,
                "representative_images": [
                    [
                        0,
                        "https://nyang-s3.s3.ap-northeast-2.amazonaws.com/jeongho/ae227aeb-81bb-4df3-9c39-9b4b861b1967.jpg",
                    ],
                ],
                "width": 340.1490478515625,
                "height": 318.1322326660156,
                "file_feature_info": [
                    [
                        "https://nyang-s3.s3.ap-northeast-2.amazonaws.com/jeongho/32e6bb48-47dc-491f-9466-8acf4534825b.png",
                        2,
                        187.75137329101562,
                        260.0215148925781,
                    ],
                    [
                        "https://nyang-s3.s3.ap-northeast-2.amazonaws.com/jeongho/951597e2-3044-42f9-964a-8d3787253d30.png",
                        2,
                        166.42271423339844,
                        215.76617431640625,
                    ],
                ],
                "closest_images": [
                    [
                        "https://nyang-s3.s3.ap-northeast-2.amazonaws.com/jeongho/9bac71f1-f0cc-4621-be7c-1b2c43e64db3.jpg",
                        "https://nyang-s3.s3.ap-northeast-2.amazonaws.com/jeongho/277a9bec-5f1a-45ef-80a2-cc91a23f0be1.jpg",
                    ],
                    [
                        "https://nyang-s3.s3.ap-northeast-2.amazonaws.com/jeongho/953dd2c6-0e35-49ba-9f90-6bcf2094ec42.png",
                        "https://nyang-s3.s3.ap-northeast-2.amazonaws.com/jeongho/174053b5-fab7-450c-91d7-9ec454a5cc29.png",
                    ],
                ],
                "tnr_info": [
                    [
                        "https://nyang-s3.s3.ap-northeast-2.amazonaws.com/jeongho/1db74885-6925-4475-b84b-27a39b7f2134.png",
                        False,
                    ],
                ],
                "tnr_count": 0,
            }
        }


class UpdateDetectModel(BaseModel):
    status: Optional[int]
    serial_number: Optional[str]
    date: Optional[str]
    num_clusters: Optional[int]
    representative_images: Optional[List[Any]]
    width: Optional[float]
    height: Optional[float]
    file_feature_info: Optional[List[Any]]
    closest_images: Optional[List[Any]]
    tnr_info: Optional[List[Any]]
    tnr_count: Optional[int]

    class Settings:
        name = "detections"

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
