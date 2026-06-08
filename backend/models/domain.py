from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class TrademarkTrend(Base):
    """
    FR-10: KIPRIS 상표 출원 데이터 캐시 테이블 (kipris_trademarks)
    FAISS 인덱스 ID가 이 테이블의 id를 참조한다.
    """
    __tablename__ = "kipris_trademarks"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    application_number = Column(String(30), nullable=False, unique=True)
    title = Column(String(255), nullable=True)
    applicant_name = Column(String(255), nullable=True)
    application_date = Column(Date, nullable=True)
    classification_code = Column(String(255), nullable=True)
    vienna_code = Column(String(255), nullable=True)
    application_status = Column(String(20), nullable=True)
    image_url = Column(Text, nullable=True)
    big_image_url = Column(Text, nullable=True)
    synced_at = Column(DateTime, nullable=True, server_default=func.current_timestamp())

    detection_results = relationship("DetectionResult", back_populates="trademark")


class DetectionHistory(Base):
    """
    FR-01-05: 업로드 파일 정보 및 탐지 요청 이력 저장 테이블
    """
    __tablename__ = "detection_history"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    input_text = Column(Text, nullable=True)
    uploaded_image_path = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("DetectionResult", back_populates="history", cascade="all, delete-orphan")


class DetectionResult(Base):
    """
    FR-02-01: 탐지 결과 및 유사도를 저장하는 테이블
    """
    __tablename__ = "detection_results"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    history_id = Column(Integer, ForeignKey("detection_history.id"), nullable=False)
    trademark_id = Column(Integer, ForeignKey("kipris_trademarks.id"), nullable=False)

    similarity_score = Column(Float, nullable=False)
    image_score = Column(Float, nullable=True)
    text_score = Column(Float, nullable=True)

    history = relationship("DetectionHistory", back_populates="results")
    trademark = relationship("TrademarkTrend", back_populates="detection_results")
