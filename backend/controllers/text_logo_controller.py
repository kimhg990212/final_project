from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.text_logo_service import generate_text_logo

router = APIRouter()

class TextLogoRequest(BaseModel):
    text: str
    user_id: Optional[int] = None
    
@router.post("/generate")
def generate_logo(request: TextLogoRequest):
    return generate_text_logo(
        user_text = request.text,
        user_id = request.user_id)
