import logging

from sqlalchemy.orm import Session

from models.download_history import DownloadHistory

logger = logging.getLogger(__name__)


def save_download_history(
    db: Session,
    user_id: int,
    prompt: str,
    image_path: str,
    result_id: int | None = None,
) -> DownloadHistory:
    if db is None:
        raise ValueError("DB session is required.")

    if not prompt or not prompt.strip():
        raise ValueError("prompt is required.")

    if not image_path or not image_path.strip():
        raise ValueError("image_path is required.")

    history = DownloadHistory(
        user_id=user_id,
        result_id=result_id,
        prompt=prompt.strip(),
        image_path=image_path.strip(),
    )

    try:
        db.add(history)
        db.commit()
        db.refresh(history)
        return history
    except Exception:
        db.rollback()
        logger.error("Failed to persist download history.", exc_info=True)
        raise
