from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class TrademarkMetadata(Base):
    """
    KIPRIS에서 직접 다운로드하여 적재할 1~2만 건의 MVP 상표 메타데이터 테이블
    """
    __tablename__ = "trademark_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    application_number = Column(String(50), unique=True, nullable=False, index=True) # 출원번호
    trademark_name = Column(String(255), nullable=False, index=True)                 # 상표명
    applicant_name = Column(String(255), nullable=True)                              # 출원인 정보
    application_date = Column(String(20), nullable=True)                             # 출원일자
    image_url = Column(String(500), nullable=False)                                  # 로고 이미지 로컬 경로 또는 URL
    keywords = Column(Text, nullable=True)                                           # 관련 키워드 (RDB 보조 검색용 프리텍스트)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # 역참조 관계 설정
    detection_results = relationship("DetectionResult", back_populates="trademark")


class DetectionHistory(Base):
    """
    FR-01-05: 업로드 파일 정보 및 탐지 요청 이력 저장 테이블
    """
    __tablename__ = "detection_history"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(String(100), nullable=False, index=True) # OAuth 2.0으로 검증된 유저 ID
    input_text = Column(Text, nullable=True)                  # 사용자가 입력한 텍스트 묘사
    uploaded_image_path = Column(String(500), nullable=True)  # 업로드된 이미지 파일 경로
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계 설정
    results = relationship("DetectionResult", back_populates="history", cascade="all, delete-orphan")


class DetectionResult(Base):
    """
    FR-02-01: 탐지 결과 및 유사도를 저장하는 테이블
    """
    __tablename__ = "detection_results"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    history_id = Column(Integer, ForeignKey("detection_history.id"), nullable=False)
    trademark_id = Column(Integer, ForeignKey("trademark_metadata.id"), nullable=False)
    
    # 최종 융합 유사도 점수 (%)
    similarity_score = Column(Float, nullable=False)
    # FR-04용: 개별 모델 기여도 점수 저장 (근거 설명용)
    image_score = Column(Float, nullable=True)
    text_score = Column(Float, nullable=True)

    # 관계 설정
    history = relationship("DetectionHistory", back_populates="results")
    trademark = relationship("TrademarkMetadata", back_populates="detection_results")