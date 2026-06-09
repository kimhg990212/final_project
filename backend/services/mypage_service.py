from datetime import datetime
from typing import List, Tuple

from sqlalchemy.orm import Session

from models.download_history import DownloadHistory
from models.schemas import DetectionHistoryItem
from models.text_to_image_result import TextToImageResult
from services.plagiarism_service import get_detection_history


def _format_timestamp(value) -> str:
    if not value:
        return ""
    return value.strftime("%Y.%m.%d %H:%M")


def _parse_timestamp(value: str) -> datetime:
    if not value:
        return datetime.min

    try:
        return datetime.strptime(value, "%Y.%m.%d %H:%M")
    except ValueError:
        return datetime.min


def _build_generation_activity(result: TextToImageResult) -> DetectionHistoryItem:
    prompt = (result.prompt or "").strip()
    description = prompt or "텍스트를 바탕으로 이미지를 생성했습니다."

    return DetectionHistoryItem(
        id=result.id,
        type="create",
        title="이미지 생성",
        description=description,
        time=_format_timestamp(result.created_at),
        downloadable=True,
        image_path=result.image_path,
        image_url=result.image_path,
    )


def _build_download_activity(history: DownloadHistory) -> DetectionHistoryItem:
    prompt = (history.prompt or "").strip()
    description = prompt or (history.image_path or "").strip() or "다운로드한 이미지를 기록했습니다."

    return DetectionHistoryItem(
        id=history.id,
        type="download",
        title="이미지 다운로드",
        description=description,
        time=_format_timestamp(history.downloaded_at),
        downloadable=True,
        image_path=history.image_path,
        image_url=history.image_path,
    )


def _sort_key(item: DetectionHistoryItem) -> Tuple[datetime, int]:
    return (_parse_timestamp(item.time), item.id)


async def get_mypage_activities(
    db: Session,
    user_id: int,
    limit: int = 24,
) -> List[DetectionHistoryItem]:
    search_activities = await get_detection_history(
        db=db,
        user_id=user_id,
        limit=limit,
    )

    generation_records = (
        db.query(TextToImageResult)
        .filter(TextToImageResult.user_id == user_id)
        .order_by(TextToImageResult.created_at.desc(), TextToImageResult.id.desc())
        .limit(limit)
        .all()
    )

    download_records = (
        db.query(DownloadHistory)
        .filter(DownloadHistory.user_id == user_id)
        .order_by(DownloadHistory.downloaded_at.desc(), DownloadHistory.id.desc())
        .limit(limit)
        .all()
    )

    create_activities = [_build_generation_activity(record) for record in generation_records]
    download_activities = [_build_download_activity(record) for record in download_records]

    activities = [*search_activities, *create_activities, *download_activities]
    activities.sort(key=_sort_key, reverse=True)

    return activities[:limit]
