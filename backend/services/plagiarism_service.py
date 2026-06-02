# backend/services/plagiarism_service.py
import math
import logging
from typing import List, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models.domain import TrademarkMetadata, DetectionHistory, DetectionResult
from backend.models.schemas import PlagiarismDetectionItem, PlagiarismExplanation
from backend.utils.faiss_handler import faiss_engine
from backend.utils.ai_inference import embed_text, embed_image

logger = logging.getLogger(__name__)

# 🌟 [수정됨] 높은 FAISS 유사도 점수를 기반으로 변별력 있는 0~1 사이 점수를 만드는 함수
def convert_raw_score_to_similarity(raw_score: float) -> float:
    """
    FAISS 원본 유사도 점수가 높을수록 최종 점수도 높아지도록 설계된 시그모이드 함수입니다.
    """
    # 🛠️ 기준점과 민감도 튜닝 (0.011 근처의 값들을 확 벌려줍니다)
    midpoint = 0.008   # 이 점수일 때 정확히 50점이 됩니다.
    steepness = 500.0  # 이 값이 클수록 1등과 2등의 점수 차이가 가파르게 벌어집니다.
    
    try:
        # 유사도용 공식: 지수 앞에 마이너스(-)가 붙어 원본 점수가 높을수록 결과가 1.0에 수렴합니다.
        sim = 1.0 / (1.0 + math.exp(-steepness * (raw_score - midpoint)))
    except OverflowError:
        sim = 1.0 if raw_score > midpoint else 0.0
        
    return sim

async def analyze_plagiarism(
    db: AsyncSession,
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
            # 🌟 올바른 유사도 변환 적용
            sim_score = convert_raw_score_to_similarity(float(raw_score))
            fusion_map[int(tm_id)] = {"text_score": sim_score, "image_score": 0.0}

    # 4-2. 이미지 벡터 검색 (100개 추출)
    if image_vector is not None:
        image_scores, image_indices = faiss_engine.search_image(image_vector, top_k=100)
        for raw_score, tm_id in zip(image_scores[0], image_indices[0]):
            if tm_id == -1: 
                continue
            target_id = int(tm_id)
            # 🌟 올바른 유사도 변환 적용
            sim_score = convert_raw_score_to_similarity(float(raw_score))
            
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
    # 6. RDB 메타데이터 조회 및 DB 안전 방어벽 설정
    # ==========================================
    metadata_map = {}
    if db is not None:
        query = select(TrademarkMetadata).where(TrademarkMetadata.id.in_(target_ids))
        result = await db.execute(query)
        metadata_records = result.scalars().all()
        metadata_map = {record.id: record for record in metadata_records}
    else:
        logger.warning("⚠️ DB 세션이 None(Mock 상태)입니다. 원본 데이터 대신 가상 상표 정보를 반환합니다.")

    # 7. 응답 데이터 포맷팅
    response_items: List[PlagiarismDetectionItem] = []
    
    for rank_item in top_results:
        tm_id = rank_item["trademark_id"]
        total_score = rank_item["total_score"]
        
        img_contrib = (rank_item["image_score"] * weight_image) / total_score * 100 if total_score > 0 else 0
        txt_contrib = (rank_item["text_score"] * weight_text) / total_score * 100 if total_score > 0 else 0
        
        tm_name = f"FAISS 검색 매칭 상표 (ID: {tm_id})"
        app_number = f"40-2026-{tm_id % 10000000:07d}"
        applicant_name = "KIPRIS 공공 데이터 출원인"
        application_date = "2026-05-29"
        image_url = f"/static/images/{tm_id}.jpg"
        matched_keywords = []

        if db is not None:
            meta = metadata_map.get(tm_id)
            if not meta: 
                continue 
            
            tm_name = meta.trademark_name
            app_number = meta.application_number
            applicant_name = meta.applicant_name
            application_date = meta.application_date
            image_url = meta.image_url
            
            if text_query and meta.keywords:
                user_words = set(text_query.split())
                db_words = set(meta.keywords.split(","))
                matched_keywords = list(user_words.intersection(db_words))
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
    db: AsyncSession,
    user_id: str,
    input_text: str,
    uploaded_image_path: str,
    detection_results: List[PlagiarismDetectionItem]
) -> int:
    if db is None:
        logger.info("DB가 아직 연결되지 않아(Mock 상태) 이력 저장을 생략합니다.")
        return 999  
        
    history = DetectionHistory(
        user_id=user_id,
        input_text=input_text,
        uploaded_image_path=uploaded_image_path
    )
    db.add(history)
    await db.flush() 

    for item in detection_results:
        result_record = DetectionResult(
            history_id=history.id,
            trademark_id=item.trademark_id,
            similarity_score=item.similarity_score,
            image_score=item.explanation.image_contribution_pct,
            text_score=item.explanation.text_contribution_pct
        )
        db.add(result_record)

    await db.commit()
    return history.id