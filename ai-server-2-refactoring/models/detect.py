from typing import List
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, Any
from .original import Original

class Detect(Original):
    class Settings:
        name = "detections"

    
class UpdateDetectModel(BaseModel):
    status: Optional[int]
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


class UpdateDetectTnrModel(BaseModel):
    status: Optional[int]
    num_clusters: Optional[int]
    representative_images: Optional[List[Any]]
    tnr_info: Optional[List[Any]]
    tnr_count: Optional[int]

    class Settings:
        name = "detections"

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
