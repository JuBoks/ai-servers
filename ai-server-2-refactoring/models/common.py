from pydantic import BaseModel
from typing import Optional, Any


class Response(BaseModel):
    status_code: int
    content: Optional[Any]

    class Config:
        schema_extra = {"example": {"status_code": 200, "content": "Sample data"}}
