import logging
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from services import plagiarism_service
from utils.file_handler import validate_file_and_save
from models.schemas import PlagiarismDetectionResponse

logger = logging.getLogger(__name__)

async def handle_plagiarism_detection(
    db: Session,
    user_id: str,
    text_query: Optional[str] = None,
    image_file: Optional[UploadFile] = None
) -> PlagiarismDetectionResponse:
    """
    도용 탐지 요청을 처리하는 컨트롤러 로직 (FR-01, FR-02, FR-04 통합)
    """
    # 1. 입력 예외 처리: 둘 다 들어오지 않은 경우
    if not text_query and not image_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="도용 탐지를 진행할 텍스트 묘사 또는 로고 이미지를 최소 하나 이상 입력해야 합니다."
        )

    saved_image_path = None
    
    # 2. 이미지 파일이 업로드된 경우 검증 및 청크 저장 수행 (FR-01-02, FR-01-04)
    if image_file and image_file.filename:
        # utils/file_handler.py의 500MB 제한 및 확장자 검증 로직 호출
        saved_image_path = await validate_file_and_save(image_file)

    try:
        # 3. 비즈니스 로직(Service) 호출하여 FAISS + RDB 검색 수행 (FR-01-07 연동)
        # 유사도 정렬, 반올림, FR-04 근거 생성이 서비스 단에서 완료되어 반환됨
        detection_items = await plagiarism_service.analyze_plagiarism(
            db=db,
            text_query=text_query,
            image_file_path=saved_image_path,
            top_k=10  # 상위 10개 출력 제한
        )

        # 4. 분석 이력 및 결과를 DB에 영구 저장 (FR-01-05)
        history_id = await plagiarism_service.save_upload_history(
            db=db,
            user_id=user_id,
            input_text=text_query,
            uploaded_image_path=saved_image_path,
            detection_results=detection_items
        )

        # 5. FR-02-02 전체 탐지 결과 요약 정보 생성
        total_found = len(detection_items)
        highest_sim = detection_items[0].similarity_score if total_found > 0 else 0.0
        print("도용 위험도: " , highest_sim)
        # 핵심 요약 문구 바인딩
        if highest_sim >= 80.0:
            summary_msg = f"경고: 기존 상표와 매우 유사한 요소가 발견되었습니다. (최고 유사도: {highest_sim}%)"
        elif highest_sim >= 50.0:
            summary_msg = f"주의: 일부 유사한 상표가 존재하므로 확인이 필요합니다. (최고 유사도: {highest_sim}%)"
        else:
            summary_msg = "안전: 입력한 정보와 크게 매칭되는 기존 도용 의심 상표가 없습니다."

        # 6. Pydantic Response 스펙에 맞춰 최종 반환 객체 빌드
        return PlagiarismDetectionResponse(
            history_id=history_id,
            requested_at=datetime.utcnow(),
            total_found=total_found,
            highest_similarity=highest_sim,
            result_summary_text=summary_msg,
            results=detection_items
        )

    except Exception as e:
        # FR-01-06: 백엔드 내부 에러 발생 시 예외 처리 및 로깅
        logger.error(f"도용 탐지 파이프라인 처리 중 에러 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 내부 분석 에러가 발생했습니다. 담당자에게 문의하세요. ({str(e)})"
        )