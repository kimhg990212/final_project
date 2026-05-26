from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from core.database import Base

class Logo(Base):

    __tablename__ = "logos"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    logo_name = Column(String)

    category = Column(String)

    image_path = Column(String)

    vector_path = Column(String)