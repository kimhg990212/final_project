from fastapi import APIRouter, Depends, File, Form, status, UploadFile
from sqlalchemy.orm import Session

from controllers.generate_controller import generate_logo_controller

from controllers.download_controller import handle_download_history
from models.user import User
from schemas.download_schema import (
    DownloadHistoryCreateRequest,
    DownloadHistoryResponse,
)
from utils.database import get_db
from utils.google_auth import require_google_user

router = APIRouter(
    prefix="/generate",
    tags=["Generate"]
)
@router.post("/logo")
async def generate_logo(
    trademark_ids: str = Form(...),
    brand_description: str = Form(...),
    style: str = Form(default=""),
):
    id_list = [int(id.strip()) for id in trademark_ids.split(",")]
    return await generate_logo_controller(
        trademark_ids=id_list,
        brand_description=brand_description,
        style=style,
    )

@router.post(
    "/download",
    response_model=DownloadHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_download_history_endpoint(
    payload: DownloadHistoryCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_google_user()),
):
    return handle_download_history(
        db=db,
        current_user_id=current_user.id,
        payload=payload,
    )
