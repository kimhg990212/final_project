import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    VERSION: str = "0.1.0"
    
    DATABASE_URL: str = "mysql+pymysql://root:your_password@localhost:3306/your_db_name"
    
    SECRET_KEY: str = "super-secret-key-please-change-it-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "uploaded_files")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    model_config = SettingsConfigDict(
        env_file=".env",           
        env_file_encoding="utf-8", 
        case_sensitive=True        
    )

settings = Settings()