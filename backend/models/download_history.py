from sqlalchemy import BigInteger, Column, DateTime, String, Text
from sqlalchemy.sql import func

from utils.database import Base


class DownloadHistory(Base):
    __tablename__ = "download_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    result_id = Column(BigInteger, nullable=True, index=True)
    prompt = Column(Text, nullable=False)
    image_path = Column(String(500), nullable=False)
    downloaded_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
