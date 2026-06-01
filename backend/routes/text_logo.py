from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from controllers.text_logo_controller import generate_logo_controller

router = APIRouter(
    prefix="/text-logo",
    tags=["Generate"]
)

class TextLogoRequest(BaseModel):
    text: str
    user_id: Optional[int] = None


@router.post("/generate")
def generate_logo(request: TextLogoRequest):
    return generate_logo_controller(request)