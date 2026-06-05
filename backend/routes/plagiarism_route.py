from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from typing import Optional

from controllers import plagiarism_controller
from models.schemas import PlagiarismDetectionResponse
from utils.database import get_db

router = APIRouter(prefix="/api/v1/detect", tags=["도용 탐지 분석 API"])

async def get_mock_current_user():
    """FR-01-08: OAuth 2.0 토큰 기반 로그인 사용자 검증 스텁"""
    return {"id": "user_minhyuk_2026", "role": "authenticated_user"}

@router.post("/", response_model=PlagiarismDetectionResponse, status_code=200)
async def detect_plagiarism_endpoint(
    text_query: Optional[str] = Form(None, description="상표명 또는 브랜드 아이디어 설명 자연어"),
    image_file: Optional[UploadFile] = File(None, description="도용 검사 대상 로고/상표 이미지 파일 (PNG, JPG)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_mock_current_user)
):
    """
    **AI 기반 통합 상표 도용 탐지 엔드포인트**
    - **Case 1 (이미지 단독):** 업로드 이미지 기반 시각적 표절 탐지
    - **Case 2 (텍스트 단독):** 입력 자연어 기반 문자 유사도 및 의미적 아이디어 탐지
    - **Case 3 (하이브리드 동시):** 이미지 유사도 + 텍스트 묘사 가중치 퓨전(6:4) 정밀 탐지
    """
    return await plagiarism_controller.handle_plagiarism_detection(
        db=db,
        user_id=current_user["id"],
        text_query=text_query,
        image_file=image_file
    )