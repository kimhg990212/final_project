from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from utils.database import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    saved_path = Column(String(500), nullable=False)
    file_type = Column(String(10))
    status = Column(String(50), default="uploaded")
    created_at = Column(DateTime, default=func.now())