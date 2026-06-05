from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from utils.database import Base


class TextToImageResult(Base):
    __tablename__ = "text_to_image_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    prompt = Column(Text, nullable=False)
    image_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())