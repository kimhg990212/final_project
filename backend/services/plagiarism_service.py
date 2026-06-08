# backend/services/plagiarism_service.py
import math
import logging
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.domain import DetectionHistory, DetectionResult, TrademarkTrend
from models.schemas import PlagiarismDetectionItem, PlagiarismExplanation
from utils.faiss_handler import faiss_engine
from utils.ai_inference import embed_text, embed_image

logger = logging.getLogger(__name__)

# 🌟 [개선됨] 높은 FAISS 유사도 점수를 기반으로 변별력 있는 0~1 사이 점수를 만드는 함수
def convert_raw_score_to_similarity(raw_score: float) -> float:
    """
    FAISS 원본 유사도 점수가 높을수록 최종 점수도 높아지도록 설계된 시그모이드 함수입니다.
    이미지 유사도 성능 개선을 위해 임계값을 조정했습니다.
    """
    # 🛠️ [개선] 기준점과 민감도 튜닝 (이미지 유사도 성능 향상)
    midpoint = 0.005   # 더 낮은 점수일 때 50점이 되도록 조정 (이미지 점수 향상)
    steepness = 800.0  # 더 가파른 곡선 (변별력 강화)
    
    try:
        # 유사도용 공식: 지수 앞에 마이너스(-)가 붙어 원본 점수가 높을수록 결과가 1.0에 수렴합니다.
        sim = 1.0 / (1.0 + math.exp(-steepness * (raw_score - midpoint)))
    except OverflowError:
        sim = 1.0 if raw_score > midpoint else 0.0
        
    return sim

async def analyze_plagiarism(
    db: Session,
    text_query: str = None,
    image_file_path: str = None,
    top_k: int = 10
) -> List[PlagiarismDetectionItem]:
    """
    동적 가중치를 적용한 하이브리드 도용 탐지 핵심 파이프라인
    """
    # 1. 초기화 (동적 가중치)
    text_vector, image_vector = None, None
    weight_text, weight_image = 0.0, 0.0

    # 2. 들어온 데이터만 임베딩 처리 및 가중치 할당
    if text_query:
        text_vector = await embed_text(text_query)
        weight_text = 1.0

    if image_file_path:
        image_vector = await embed_image(image_file_path)
        weight_image = 1.0

    # 3. 둘 다 들어온 경우 가중치 분배 (Late Fusion)
    if text_vector is not None and image_vector is not None:
        weight_image = 0.6  
        weight_text = 0.4   

    # 4. FAISS 검색 수행 및 결과 병합 (Union Map 생성)
    fusion_map: Dict[int, Dict[str, float]] = {}

    # 4-1. 텍스트 벡터 검색 (100개 추출)
    if text_vector is not None:
        text_scores, text_indices = faiss_engine.search_text(text_vector, top_k=100)
        for raw_score, tm_id in zip(text_scores[0], text_indices[0]):
            if tm_id == -1:
                continue
            # faiss_handler에서 이미 1/(1+d) 변환 완료 → 그대로 사용
            sim_score = float(raw_score)
            fusion_map[int(tm_id)] = {"text_score": sim_score, "image_score": 0.0}

    # 4-2. 이미지 벡터 검색 (100개 추출)
    if image_vector is not None:
        image_scores, image_indices = faiss_engine.search_image(image_vector, top_k=100)
        for raw_score, tm_id in zip(image_scores[0], image_indices[0]):
            if tm_id == -1:
                continue
            target_id = int(tm_id)
            # faiss_handler에서 이미 1/(1+d) 변환 완료 → 그대로 사용
            sim_score = float(raw_score)
            
            if target_id not in fusion_map:
                fusion_map[target_id] = {"text_score": 0.0, "image_score": 0.0}
            fusion_map[target_id]["image_score"] = sim_score

    # 5. 최종 가중치 합산 (Total Score 계산)
    final_rankings = []
    for tm_id, scores in fusion_map.items():
        s_text = scores["text_score"] 
        s_img = scores["image_score"]
        
        total_score = ((s_text * weight_text) + (s_img * weight_image)) * 100
        
        final_rankings.append({
            "trademark_id": tm_id,
            "total_score": total_score,
            "text_score": s_text * 100,
            "image_score": s_img * 100
        })

    # 유사도가 가장 높은 순서대로 상위 정렬 (reverse=True 유지)
    final_rankings.sort(key=lambda x: x["total_score"], reverse=True)
    top_results = final_rankings[:top_k]
    target_ids = [item["trademark_id"] for item in top_results]

    if not target_ids:
        return []

    # ==========================================
    # 6. RDB 메타데이터 조회 (trademark_trends 테이블)
    # ==========================================
    metadata_map = {}
    if db is not None:
        query = select(TrademarkTrend).where(TrademarkTrend.id.in_(target_ids))
        result = db.execute(query)
        metadata_records = result.scalars().all()
        metadata_map = {record.id: record for record in metadata_records}
    else:
        logger.warning("⚠️ DB 세션이 None(Mock 상태)입니다. 원본 데이터 대신 가상 상표 정보를 반환합니다.")

    # 7. 응답 데이터 포맷팅
    response_items: List[PlagiarismDetectionItem] = []

    for rank_item in top_results:
        tm_id = rank_item["trademark_id"]
        total_score = rank_item["total_score"]

        weighted_text = rank_item["text_score"] * weight_text
        weighted_image = rank_item["image_score"] * weight_image
        total_weighted = weighted_text + weighted_image

        if total_weighted > 0:
            img_contrib = (weighted_image / total_weighted) * 100
            txt_contrib = (weighted_text / total_weighted) * 100
        else:
            img_contrib = 0.0
            txt_contrib = 0.0

        tm_name = f"FAISS 검색 매칭 상표 (ID: {tm_id})"
        app_number = f"40-2026-{tm_id % 10000000:07d}"
        applicant_name = "KIPRIS 공공 데이터 출원인"
        application_date = ""
        image_url = ""
        matched_keywords = []

        if db is not None:
            meta = metadata_map.get(tm_id)
            if not meta:
                continue

            tm_name = meta.title or f"상표 ID {tm_id}"
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
                # datetime.date 또는 datetime.datetime 객체
                application_date = raw_date.strftime("%Y-%m-%d")
            image_url = meta.image_url or meta.big_image_url or ""

            if text_query:
                user_words = set(text_query.split())
                db_text = f"{meta.title or ''}"
                db_words = set(db_text.split())
                matched_keywords = [w for w in user_words if w in db_words and len(w) > 1]
        else:
            if text_query:
                matched_keywords = [word for word in text_query.split() if len(word) > 1]

        if weight_image > 0 and weight_text > 0:
            summary_text = "이미지 형태와 텍스트 문맥이 모두 분석되었습니다."
        elif weight_image > 0:
            summary_text = "시각적 형태를 기준으로 유사도가 산출되었습니다."
        else:
            summary_text = "상표명 및 묘사 텍스트를 기준으로 유사도가 산출되었습니다."

        explanation = PlagiarismExplanation(
            summary=summary_text,
            image_contribution_pct=round(img_contrib, 1),
            text_contribution_pct=round(txt_contrib, 1),
            keyword_matched=matched_keywords
        )

        item = PlagiarismDetectionItem(
            trademark_id=tm_id,
            trademark_name=tm_name,
            application_number=app_number,
            applicant_name=applicant_name,
            application_date=application_date,
            image_url=image_url,
            similarity_score=round(total_score, 1), 
            explanation=explanation
        )
        response_items.append(item)

    return response_items

async def save_upload_history(
    db: Session,
    user_id: str,
    input_text: str,
    uploaded_image_path: str,
    detection_results: List[PlagiarismDetectionItem]
) -> int:
    # detection_history / detection_results 테이블은 인증 담당 팀이 생성 전
    # 테이블 준비될 때까지 mock 유지 (999 반환)
    logger.info("이력 저장은 인증 테이블 생성 전까지 Mock 상태로 유지합니다.")
    return 999
