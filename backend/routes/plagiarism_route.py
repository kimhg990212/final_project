from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional

from controllers import plagiarism_controller
from models.schemas import DetectionHistoryItem, PlagiarismDetectionResponse
from models.user import User
from services import plagiarism_service
from utils.database import get_db
from utils.google_auth import require_google_user

router = APIRouter(prefix="/api/v1/detect", tags=["detect"])


@router.get("/history", response_model=List[DetectionHistoryItem], status_code=200)
async def get_detection_history_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_google_user()),
):
    return await plagiarism_service.get_detection_history(
        db=db,
        user_id=current_user.id,
        limit=24,
    )


@router.post("/", response_model=PlagiarismDetectionResponse, status_code=200)
async def detect_plagiarism_endpoint(
    text_query: Optional[str] = Form(None, description="Text query"),
    image_file: Optional[UploadFile] = File(None, description="Image file"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_google_user()),
):
    return await plagiarism_controller.handle_plagiarism_detection(
        db=db,
        user_id=current_user.id,
        text_query=text_query,
        image_file=image_file,
    )
