#  result_model.py - DB테이블 정의
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from utils.database import Base

# GeneratedResult → generated_results 테이블(AI 생성 완료되면 어떤 파일로, 어떤 프롬프트로, 결과 텍스트가 뭔지 저장)
class GeneratedResult(Base):
    __tablename__ = "generated_results"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, nullable=False)
    prompt = Column(Text)
    result_text = Column(Text)
    created_at = Column(DateTime, default=func.now())