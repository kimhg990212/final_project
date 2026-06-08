from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from schemas.download_schema import DownloadHistoryCreateRequest
from services.download_service import save_download_history


def handle_download_history(
    db: Session,
    current_user_id: int,
    payload: DownloadHistoryCreateRequest,
):
    if payload.user_id is not None and payload.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user_id does not match authenticated user.",
        )

    history = save_download_history(
        db=db,
        user_id=current_user_id,
        result_id=payload.result_id,
        prompt=payload.prompt,
        image_path=payload.image_path,
    )

    return {
        "id": history.id,
        "user_id": history.user_id,
        "result_id": history.result_id,
        "prompt": history.prompt,
        "image_path": history.image_path,
        "downloaded_at": history.downloaded_at,
    }
