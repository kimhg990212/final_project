from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from utils.database import Base

class GeneratedResult(Base):
    __tablename__ = "generated_results"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, nullable=False)
    prompt = Column(Text)
    result_image = Column(Text)
    created_at = Column(DateTime, default=func.now())