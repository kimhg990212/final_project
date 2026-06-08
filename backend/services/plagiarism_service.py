import logging
import math
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from models.domain import DetectionHistory, DetectionResult, TrademarkTrend
from models.schemas import (
    DetectionHistoryItem,
    DetectionHistoryResultItem,
    PlagiarismDetectionItem,
    PlagiarismExplanation,
)
from utils.ai_inference import embed_image, embed_text
from utils.faiss_handler import faiss_engine

logger = logging.getLogger(__name__)


def convert_raw_score_to_similarity(raw_score: float) -> float:
    midpoint = 0.005
    steepness = 800.0

    try:
        return 1.0 / (1.0 + math.exp(-steepness * (raw_score - midpoint)))
    except OverflowError:
        return 1.0 if raw_score > midpoint else 0.0


async def analyze_plagiarism(
    db: Session,
    text_query: str = None,
    image_file_path: str = None,
    top_k: int = 10,
) -> List[PlagiarismDetectionItem]:
    text_vector, image_vector = None, None
    weight_text, weight_image = 0.0, 0.0

    if text_query:
        text_vector = await embed_text(text_query)
        weight_text = 1.0

    if image_file_path:
        image_vector = await embed_image(image_file_path)
        weight_image = 1.0

    if text_vector is not None and image_vector is not None:
        weight_text = 0.4
        weight_image = 0.6

    fusion_map: Dict[int, Dict[str, float]] = {}

    if text_vector is not None:
        text_scores, text_indices = faiss_engine.search_text(text_vector, top_k=100)
        for raw_score, tm_id in zip(text_scores[0], text_indices[0]):
            if tm_id == -1:
                continue
            fusion_map[int(tm_id)] = {"text_score": float(raw_score), "image_score": 0.0}

    if image_vector is not None:
        image_scores, image_indices = faiss_engine.search_image(image_vector, top_k=100)
        for raw_score, tm_id in zip(image_scores[0], image_indices[0]):
            if tm_id == -1:
                continue
            target_id = int(tm_id)
            if target_id not in fusion_map:
                fusion_map[target_id] = {"text_score": 0.0, "image_score": 0.0}
            fusion_map[target_id]["image_score"] = float(raw_score)

    final_rankings = []
    for tm_id, scores in fusion_map.items():
        s_text = scores["text_score"]
        s_img = scores["image_score"]
        weighted_text_score = s_text * weight_text
        weighted_image_score = s_img * weight_image
        total_score = (weighted_text_score + weighted_image_score) * 100

        final_rankings.append(
            {
                "trademark_id": tm_id,
                "total_score": total_score,
                "text_score": weighted_text_score * 100,
                "image_score": weighted_image_score * 100,
            }
        )

    final_rankings.sort(key=lambda x: x["total_score"], reverse=True)
    top_results = final_rankings[:top_k]
    target_ids = [item["trademark_id"] for item in top_results]

    if not target_ids:
        return []

    metadata_map = {}
    if db is not None:
        result = db.execute(select(TrademarkTrend).where(TrademarkTrend.id.in_(target_ids)))
        metadata_map = {record.id: record for record in result.scalars().all()}
    else:
        logger.warning("DB session is None, returning synthesized trademark metadata.")

    response_items: List[PlagiarismDetectionItem] = []
    for rank_item in top_results:
        tm_id = rank_item["trademark_id"]
        total_score = rank_item["total_score"]
        text_score = round(rank_item["text_score"], 1)
        image_score = round(rank_item["image_score"], 1)

        weighted_text = rank_item["text_score"]
        weighted_image = rank_item["image_score"]
        total_weighted = weighted_text + weighted_image

        if total_weighted > 0:
            img_contrib = (weighted_image / total_weighted) * 100
            txt_contrib = (weighted_text / total_weighted) * 100
        else:
            img_contrib = 0.0
            txt_contrib = 0.0

        tm_name = f"FAISS matched trademark (ID: {tm_id})"
        app_number = f"40-2026-{tm_id % 10000000:07d}"
        applicant_name = "KIPRIS public data"
        application_date = ""
        image_url = ""
        matched_keywords = []

        if db is not None:
            meta = metadata_map.get(tm_id)
            if not meta:
                continue

            tm_name = meta.title or f"Trademark ID {tm_id}"
            app_number = meta.application_number
            applicant_name = meta.applicant_name or ""

            raw_date = meta.application_date
            if raw_date is None:
                application_date = ""
            elif isinstance(raw_date, str):
                if len(raw_date) == 8 and raw_date.isdigit():
                    application_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                else:
                    application_date = raw_date
            else:
                application_date = raw_date.strftime("%Y-%m-%d")

            image_url = meta.image_url or meta.big_image_url or ""

            if text_query:
                user_words = set(text_query.split())
                db_words = set((meta.title or "").split())
                matched_keywords = [w for w in user_words if w in db_words and len(w) > 1]
        else:
            if text_query:
                matched_keywords = [word for word in text_query.split() if len(word) > 1]

        if weight_image > 0 and weight_text > 0:
            summary_text = "이미지와 텍스트를 함께 분석했습니다."
        elif weight_image > 0:
            summary_text = "이미지 기반 유사도 검색을 수행했습니다."
        else:
            summary_text = "상표명과 텍스트 기반 유사도 검색을 수행했습니다."

        explanation = PlagiarismExplanation(
            summary=summary_text,
            image_contribution_pct=round(img_contrib, 1),
            text_contribution_pct=round(txt_contrib, 1),
            keyword_matched=matched_keywords,
        )

        response_items.append(
            PlagiarismDetectionItem(
                trademark_id=tm_id,
                trademark_name=tm_name,
                application_number=app_number,
                applicant_name=applicant_name,
                application_date=application_date,
                image_url=image_url,
                similarity_score=round(total_score, 1),
                text_score=text_score,
                image_score=image_score,
                explanation=explanation,
            )
        )

    return response_items


async def save_upload_history(
    db: Session,
    user_id: str,
    input_text: str,
    uploaded_image_path: str,
    detection_results: List[PlagiarismDetectionItem],
) -> int:
    if db is None:
        logger.warning("DB session is None, skipping history persistence.")
        return 999

    try:
        history = DetectionHistory(
            user_id=str(user_id),
            input_text=input_text,
            uploaded_image_path=uploaded_image_path,
        )
        db.add(history)
        db.flush()

        result_rows = [
            DetectionResult(
                history_id=history.id,
                trademark_id=item.trademark_id,
                similarity_score=item.similarity_score,
                image_score=item.image_score,
                text_score=item.text_score,
            )
            for item in detection_results
        ]

        if result_rows:
            db.add_all(result_rows)

        db.commit()
        db.refresh(history)
        return history.id
    except Exception:
        db.rollback()
        logger.error("Failed to persist detection history/results.", exc_info=True)
        raise


async def get_detection_history(
    db: Session,
    user_id: str,
    limit: int = 24,
) -> List[DetectionHistoryItem]:
    if db is None:
        return []

    histories = (
        db.query(DetectionHistory)
        .options(joinedload(DetectionHistory.results).joinedload(DetectionResult.trademark))
        .filter(DetectionHistory.user_id == str(user_id))
        .order_by(DetectionHistory.created_at.desc(), DetectionHistory.id.desc())
        .limit(limit)
        .all()
    )

    items: List[DetectionHistoryItem] = []
    for history in histories:
        results = sorted(
            list(history.results or []),
            key=lambda result: result.similarity_score or 0.0,
            reverse=True,
        )
        total_found = len(results)
        highest_similarity = max((result.similarity_score for result in results), default=0.0)
        created_at = history.created_at.strftime("%Y.%m.%d %H:%M") if history.created_at else ""
        input_text = history.input_text.strip() if history.input_text else None

        description = f"Highest similarity {highest_similarity:.1f}% | {total_found} results"
        if input_text:
            description = f"{input_text} | {description}"

        detail_items: List[DetectionHistoryResultItem] = []
        for result in results:
            trademark = result.trademark
            application_date = None
            if trademark and trademark.application_date is not None:
                application_date = trademark.application_date.strftime("%Y-%m-%d")

            detail_items.append(
                DetectionHistoryResultItem(
                    trademark_id=result.trademark_id,
                    title=trademark.title if trademark else None,
                    applicant_name=trademark.applicant_name if trademark else None,
                    application_date=application_date,
                    application_status=trademark.application_status if trademark else None,
                    image_url=(trademark.image_url or trademark.big_image_url) if trademark else None,
                    similarity_score=round(result.similarity_score or 0.0, 1),
                    text_score=round(result.text_score, 1) if result.text_score is not None else None,
                    image_score=round(result.image_score, 1) if result.image_score is not None else None,
                )
            )

        items.append(
            DetectionHistoryItem(
                id=history.id,
                type="search",
                title="Search history",
                description=description,
                time=created_at,
                downloadable=True,
                history_id=history.id,
                total_found=total_found,
                highest_similarity=round(highest_similarity, 1),
                input_text=input_text,
                results=detail_items,
            )
        )

    return items
