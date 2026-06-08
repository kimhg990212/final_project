from sqlalchemy import Column, Integer, String, DateTime
from utils.database import Base

class KiprisTrademark(Base):
    __tablename__ = "kipris_trademarks"

    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String(50))
    title = Column(String(255))
    applicant_name = Column(String(255))
    application_date = Column(String(20))
    classification_code = Column(String(100))
    vienna_code = Column(String(100))
    application_status = Column(String(100))
    image_url = Column(String(500))
    big_image_url = Column(String(500))
    synced_at = Column(DateTime)