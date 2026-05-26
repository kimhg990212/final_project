import os
from sqlalchemy import create_engine

user_id  = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host     = os.getenv("DB_HOST", "localhost")   
port     = os.getenv("DB_PORT") 
db_name  = os.getenv("MYSQL_DATABASE")
db_info = f"mysql+pymysql://{user_id}:{password}@{host}:{port}/{db_name}"
engine = create_engine(db_info, connect_args={"charset": "utf8mb4"})