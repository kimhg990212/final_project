from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, text
from utils.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_sub = Column(String(64), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    nickname = Column(String(100))
    role = Column(String(20), default="USER")
    is_deleted = Column(Boolean, default=False)
    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
    
