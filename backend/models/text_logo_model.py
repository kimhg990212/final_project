from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

# 사용자별로 생성된 이미지 히스토리 저장을 위한 스키마
class TextLogoHistory(BaseModel):
    id: Optional[int] = None
    user_id: int

    user_text: str
    keywords: Dict
    generated_prompt: str
    image_url: str

    created_at: datetime = datetime.now()
    