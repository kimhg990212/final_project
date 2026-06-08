from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DownloadHistoryCreateRequest(BaseModel):
    user_id: Optional[int] = Field(None, description="Authenticated user id for validation")
    result_id: Optional[int] = Field(None, description="Generated result id")
    prompt: str = Field(..., description="Prompt used to generate the image")
    image_path: str = Field(..., description="Saved image path")


class DownloadHistoryResponse(BaseModel):
    id: int
    user_id: int
    result_id: Optional[int] = None
    prompt: str
    image_path: str
    downloaded_at: datetime
