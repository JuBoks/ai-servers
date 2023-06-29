from pydantic import BaseModel
from typing import Optional, Any


class Response(BaseModel):
    status_code: int = 500
    content: Optional[Any] = None

    class Config:
        schema_extra = {"example": {"status_code": 200, "content": "Sample data"}}
