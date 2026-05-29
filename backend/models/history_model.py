from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from core.database import Base

class History(Base):

    __tablename__ = "history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    prompt = Column(String)

    category = Column(String)

    image_path = Column(String)

    result_image1 = Column(String)

    result_image2 = Column(String)