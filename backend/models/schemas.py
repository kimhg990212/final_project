from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ==========================================
# FR-02 & FR-04: 탐지 결과 출력을 위한 Response 스펙
# ==========================================

class PlagiarismExplanation(BaseModel):
    """
    FR-04: 탐지 근거 설명 스펙 (개발 및 AI 관점의 설명 조합)
    """
    summary: str = Field(..., description="탐지 결과에 대한 AI/개발 종합 분석 요약")
    image_contribution_pct: Optional[float] = Field(None, description="이미지 유사도가 기여한 비율 (%)")
    text_contribution_pct: Optional[float] = Field(None, description="텍스트 문맥 유사도가 기여한 비율 (%)")
    keyword_matched: List[str] = Field(default=[], description="사용자 입력 키워드와 KIPRIS 메타데이터가 매칭된 단어 목록")

class PlagiarismDetectionItem(BaseModel):
    """
    FR-02-01, FR-02-03: 유사 상품 개별 항목 상세 정보
    """
    trademark_id: int
    trademark_name: str                                    # 상표명
    application_number: str                                # 출원번호 (상세 메타정보)
    applicant_name: Optional[str]                          # 출원인 정보 (상세 메타정보)
    application_date: Optional[str]                        # 출원정보 (상세 메타정보)
    image_url: str                                         # 시각화용 이미지 URL
    similarity_score: float = Field(..., example=85.4)    # 소수점 둘째자리에서 반올림된 최종 유사도 (%)
    
    # FR-04: 이 항목이 왜 유사한지에 대한 근거 설명 데이터 구조 포함
    explanation: PlagiarismExplanation

class PlagiarismDetectionResponse(BaseModel):
    """
    FR-02-02: 탐지 결과 전체 요약 및 목록 응답 래퍼
    """
    history_id: int
    requested_at: datetime
    total_found: int
    highest_similarity: float = Field(..., description="최고 유사도 수치")
    
    # FR-02-02: 핵심 요약 정보 문구
    result_summary_text: str = Field(..., description="전체 결과에 대한 한 줄 요약")
    
    # FR-02-01: 유사도 순으로 정렬되어 반환될 목록
    results: List[PlagiarismDetectionItem]