import uuid
import os
import shutil
from fastapi import UploadFile, HTTPException
from config import settings 

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".txt", ".docx"}

async def save_upload_file(file: UploadFile) -> dict:
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="허용되지 않는 파일 형식입니다.")
    
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기가 10MB를 초과했습니다.")
    await file.seek(0)
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, unique_filename) # UPLOAD_DIR: config 설정값
     
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "filename": file.filename,
        "saved_path": save_path,
        "file_type": ext
    }