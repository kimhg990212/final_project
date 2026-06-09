import logging
import math
import re
from difflib import SequenceMatcher
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
from utils.llm_explanation import generate_detection_reason

logger = logging.getLogger(__name__)


def _normalize_trademark_name(value: str) -> str:
    if not value:
        return ""
    return re.sub(r"[^0-9a-zA-Z가-힣]", "", value).lower()


def _levenshtein_distance(left: str, right: str) -> int:
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)

    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (left_char != right_char)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    return previous[-1]


def _calculate_name_similarity(query_name: str, target_name: str) -> float:
    query = _normalize_trademark_name(query_name)
    target = _normalize_trademark_name(target_name)

    if not query or not target:
        return 0.0
    if query == target:
        return 100.0

    sequence_score = SequenceMatcher(None, query, target).ratio() * 100
    distance = _levenshtein_distance(query, target)
    distance_score = (1 - (distance / max(len(query), len(target)))) * 100

    if distance == 1 and max(len(query), len(target)) <= 4:
        distance_score = max(distance_score, 86.0)

    if query in target or target in query:
        containment_score = (min(len(query), len(target)) / max(len(query), len(target))) * 100
    else:
        containment_score = 0.0

    return round(max(sequence_score, distance_score, containment_score), 1)


def _get_component_weights(has_name: bool, has_description: bool, has_image: bool) -> Dict[str, float]:
    if has_name and has_description and has_image:
        return {"name": 0.45, "description": 0.25, "image": 0.30}
    if has_name and has_description:
        return {"name": 0.60, "description": 0.40, "image": 0.0}
    if has_name and has_image:
        return {"name": 0.50, "description": 0.0, "image": 0.50}
    if has_description and has_image:
        return {"name": 0.0, "description": 0.40, "image": 0.60}
    if has_name:
        return {"name": 1.0, "description": 0.0, "image": 0.0}
    if has_description:
        return {"name": 0.0, "description": 1.0, "image": 0.0}
    if has_image:
        return {"name": 0.0, "description": 0.0, "image": 1.0}
    return {"name": 0.0, "description": 0.0, "image": 0.0}


def _get_strong_match_blend_weight(strongest_score_pct: float) -> float:
    if strongest_score_pct >= 90:
        return 0.75
    if strongest_score_pct >= 80:
        return 0.60
    if strongest_score_pct >= 70:
        return 0.40
    if strongest_score_pct >= 60:
        return 0.25
    if strongest_score_pct >= 50:
        return 0.10
    return 0.0


def _calculate_final_score(
    *,
    name_score_pct: float,
    description_score_pct: float,
    image_score_pct: float,
    weights: Dict[str, float],
    has_name: bool,
    has_image: bool,
) -> float:
    base_score = (
        (name_score_pct * weights["name"])
        + (description_score_pct * weights["description"])
        + (image_score_pct * weights["image"])
    )

    if not (has_name and has_image):
        return base_score

    strongest_score = max(name_score_pct, image_score_pct)
    strong_match_weight = _get_strong_match_blend_weight(strongest_score)
    if strong_match_weight == 0:
        return base_score

    return (strongest_score * strong_match_weight) + (base_score * (1 - strong_match_weight))


def _calculate_display_contributions(
    *,
    name_score_pct: float,
    description_score_pct: float,
    image_score_pct: float,
    weights: Dict[str, float],
    has_name: bool,
    has_image: bool,
) -> Dict[str, float]:
    weighted_name = (name_score_pct * weights["name"]) + (
        description_score_pct * weights["description"]
    )
    weighted_image = image_score_pct * weights["image"]

    if has_name and has_image:
        strongest_score = max(name_score_pct, image_score_pct)
        strong_match_weight = _get_strong_match_blend_weight(strongest_score)
        if strong_match_weight > 0:
            weighted_name *= 1 - strong_match_weight
            weighted_image *= 1 - strong_match_weight

            if name_score_pct >= image_score_pct:
                weighted_name += strongest_score * strong_match_weight
            else:
                weighted_image += strongest_score * strong_match_weight

    total_weighted = weighted_name + weighted_image
    if total_weighted <= 0:
        return {"name": 0.0, "image": 0.0}

    return {
        "name": (weighted_name / total_weighted) * 100,
        "image": (weighted_image / total_weighted) * 100,
    }


def convert_raw_score_to_similarity(raw_score: float) -> float:
    midpoint = 0.005
    steepness = 800.0

    try:
        return 1.0 / (1.0 + math.exp(-steepness * (raw_score - midpoint)))
    except OverflowError:
        return 1.0 if raw_score > midpoint else 0.0


async def analyze_plagiarism(
    db: Session,
    trademark_name: str = None,
    description_query: str = None,
    text_query: str = None,
    image_file_path: str = None,
    top_k: int = 10,
) -> List[PlagiarismDetectionItem]:
    description_text = description_query or text_query
    input_text_for_reason = " / ".join(
        text for text in [trademark_name, description_text] if text
    )

    has_name = bool(trademark_name)
    has_description = bool(description_text)
    has_image = bool(image_file_path)
    weights = _get_component_weights(has_name, has_description, has_image)

    description_vector, image_vector = None, None

    if description_text:
        description_vector = await embed_text(description_text)

    if image_file_path:
        image_vector = await embed_image(image_file_path)

    fusion_map: Dict[int, Dict[str, float]] = {}

    if trademark_name and db is not None:
        name_rows = db.execute(
            select(TrademarkTrend.id, TrademarkTrend.title).where(TrademarkTrend.title.isnot(None))
        ).all()

        for tm_id, title in name_rows:
            name_score = _calculate_name_similarity(trademark_name, title)
            if name_score < 35.0:
                continue
            fusion_map[int(tm_id)] = {
                "name_score": name_score / 100,
                "description_score": 0.0,
                "image_score": 0.0,
            }

    if description_vector is not None:
        text_scores, text_indices = faiss_engine.search_text(description_vector, top_k=100)
        for raw_score, tm_id in zip(text_scores[0], text_indices[0]):
            if tm_id == -1:
                continue
            target_id = int(tm_id)
            if target_id not in fusion_map:
                fusion_map[target_id] = {
                    "name_score": 0.0,
                    "description_score": 0.0,
                    "image_score": 0.0,
                }
            fusion_map[target_id]["description_score"] = float(raw_score)

    if image_vector is not None:
        image_scores, image_indices = faiss_engine.search_image(image_vector, top_k=100)
        for raw_score, tm_id in zip(image_scores[0], image_indices[0]):
            if tm_id == -1:
                continue
            target_id = int(tm_id)
            if target_id not in fusion_map:
                fusion_map[target_id] = {
                    "name_score": 0.0,
                    "description_score": 0.0,
                    "image_score": 0.0,
                }
            fusion_map[target_id]["image_score"] = max(
                fusion_map[target_id]["image_score"],
                float(raw_score),
            )

    final_rankings = []
    for tm_id, scores in fusion_map.items():
        name_score_pct = scores["name_score"] * 100
        description_score_pct = scores["description_score"] * 100
        image_score_pct = scores["image_score"] * 100
        weighted_text_score = (
            name_score_pct * weights["name"]
        ) + (
            description_score_pct * weights["description"]
        )
        weighted_image_score = image_score_pct * weights["image"]
        total_score = _calculate_final_score(
            name_score_pct=name_score_pct,
            description_score_pct=description_score_pct,
            image_score_pct=image_score_pct,
            weights=weights,
            has_name=has_name,
            has_image=has_image,
        )

        final_rankings.append(
            {
                "trademark_id": tm_id,
                "total_score": total_score,
                "name_score": name_score_pct,
                "description_score": description_score_pct,
                "text_score": weighted_text_score,
                "image_score": image_score_pct,
                "weighted_image_score": weighted_image_score,
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
        image_score = round(rank_item["weighted_image_score"], 1)

        contributions = _calculate_display_contributions(
            name_score_pct=rank_item["name_score"],
            description_score_pct=rank_item["description_score"],
            image_score_pct=rank_item["image_score"],
            weights=weights,
            has_name=has_name,
            has_image=has_image,
        )
        name_contrib = contributions["name"]
        img_contrib = contributions["image"]
        txt_contrib = name_contrib
        desc_contrib = 0.0

        tm_name = f"FAISS matched trademark (ID: {tm_id})"
        app_number = f"40-2026-{tm_id % 10000000:07d}"
        applicant_name = "KIPRIS public data"
        application_date = ""
        image_url = ""
        ocr_text = ""
        caption = ""
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
            ocr_text = getattr(meta, "ocr_text", "") or ""
            caption = getattr(meta, "caption", "") or ""

            if description_text or trademark_name:
                user_words = set((input_text_for_reason or "").split())
                db_text = f"{meta.title or ''} {ocr_text}"
                db_words = set(db_text.split())
                matched_keywords = [w for w in user_words if w in db_words and len(w) > 1]
        else:
            if input_text_for_reason:
                matched_keywords = [word for word in input_text_for_reason.split() if len(word) > 1]

        if weights["name"] > 0 and weights["description"] > 0 and weights["image"] > 0:
            summary_text = "상표명 문자 유사도, 추가 설명의 의미, 이미지 형태가 모두 분석되었습니다."
        elif weights["name"] > 0 and weights["description"] > 0:
            summary_text = "상표명 문자 유사도와 추가 설명의 의미가 함께 분석되었습니다."
        elif weights["name"] > 0 and weights["image"] > 0:
            summary_text = "상표명 문자 유사도와 이미지 형태가 함께 분석되었습니다."
        elif weights["description"] > 0 and weights["image"] > 0:
            summary_text = "추가 설명의 의미와 이미지 형태가 함께 분석되었습니다."
        elif weights["image"] > 0:
            summary_text = "시각적 형태를 기준으로 유사도가 산출되었습니다."
        elif weights["name"] > 0:
            summary_text = "상표명 글자 자체의 유사도를 기준으로 산출되었습니다."
        else:
            summary_text = "추가 설명의 의미적 묘사를 기준으로 유사도가 산출되었습니다."

        llm_reason = await generate_detection_reason(
            trademark_name_query=trademark_name,
            description_query=description_text,
            text_query=input_text_for_reason,
            uploaded_image_path=image_file_path,
            trademark_name=tm_name,
            application_number=app_number,
            trademark_image_url=image_url,
            ocr_text=ocr_text,
            caption=caption,
            name_score=rank_item["name_score"],
            description_score=rank_item["description_score"],
            text_score=rank_item["text_score"],
            image_score=rank_item["image_score"],
            total_score=total_score,
            image_contribution_pct=img_contrib,
            text_contribution_pct=txt_contrib,
            name_contribution_pct=name_contrib,
            description_contribution_pct=desc_contrib,
            matched_keywords=matched_keywords,
        )

        explanation = PlagiarismExplanation(
            summary=summary_text,
            image_contribution_pct=round(img_contrib, 1),
            text_contribution_pct=round(txt_contrib, 1),
            name_contribution_pct=round(name_contrib, 1),
            description_contribution_pct=round(desc_contrib, 1),
            keyword_matched=matched_keywords,
            image_reason=llm_reason["image_reason"],
            text_reason=llm_reason["text_reason"],
            llm_generated=llm_reason["llm_generated"],
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
