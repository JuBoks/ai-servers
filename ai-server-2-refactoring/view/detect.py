from typing import List
from pydantic import BaseModel


class DetectRepresentativeView(BaseModel):
    serial_number: str
    date: str
    representative_images: List


class DetectStatusView(BaseModel):
    serial_number: str
    date: str
    status: int


class DetectTnrView(BaseModel):
    status: int
    num_clusters: int
    representative_images: List
    tnr_info: List
    tnr_count: int

