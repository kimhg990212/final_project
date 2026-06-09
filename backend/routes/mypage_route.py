from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.schemas import DetectionHistoryItem
from models.user import User
from services.mypage_service import get_mypage_activities
from utils.database import get_db
from utils.google_auth import require_google_user

router = APIRouter(prefix="/api/v1/mypage", tags=["mypage"])


@router.get("/activities", response_model=List[DetectionHistoryItem], status_code=200)
async def get_mypage_activities_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_google_user()),
):
    return await get_mypage_activities(
        db=db,
        user_id=current_user.id,
        limit=24,
    )
