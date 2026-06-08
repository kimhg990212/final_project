from typing import List

from sqlalchemy.orm import Session

from models.schemas import DetectionHistoryItem
from models.text_to_image_result import TextToImageResult
from services.plagiarism_service import get_detection_history


def _format_timestamp(value) -> str:
    if not value:
        return ""
    return value.strftime("%Y.%m.%d %H:%M")


def _build_generation_activity(result: TextToImageResult) -> DetectionHistoryItem:
    prompt = (result.prompt or "").strip()
    description = prompt or "텍스트를 기반으로 이미지를 생성했습니다."

    return DetectionHistoryItem(
        id=result.id,
        type="create",
        title="이미지 생성",
        description=description,
        time=_format_timestamp(result.created_at),
        downloadable=True,
        image_path=result.image_path,
    )


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

    create_activities = [_build_generation_activity(record) for record in generation_records]

    activities = [*search_activities, *create_activities]
    activities.sort(key=lambda item: item.time or "", reverse=True)

    return activities[:limit]
