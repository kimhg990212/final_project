import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

user_id  = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host     = os.getenv("DB_HOST", "localhost")   
port     = os.getenv("DB_PORT", "3306")
db_name  = os.getenv("MYSQL_DATABASE")

db_info = f"mysql+pymysql://{user_id}:{password}@{host}:{port}/{db_name}"
engine = create_engine(db_info, connect_args={"charset": "utf8mb4"})


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

#API 요청마다 DB 연결 생성/종료
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()