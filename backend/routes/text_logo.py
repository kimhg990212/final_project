from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from utils.database import get_db
from controllers.text_logo_controller import generate_logo_controller

router = APIRouter(
    prefix="/text-logo",
    tags=["Generate"]
)

class TextLogoRequest(BaseModel):
    logo_name: str
    text: str
    user_id: int

@router.post("/generate")
def generate_logo(
    request: TextLogoRequest,
    db: Session = Depends(get_db)
):
    return generate_logo_controller(request, db)