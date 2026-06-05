from fastapi import APIRouter, UploadFile,BackgroundTasks, File, Depends
from sqlalchemy.orm import Session
from utils.database import get_db
from controllers.upload_controllers import (
    handle_upload,
    handle_generate,
    handle_get_result
)
from utils.response_utils import GenerateRequest

router = APIRouter(tags=["FR-07 업로드 자료 기반 생성"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await handle_upload(file, db)

@router.post("/generate")
def generate_content(req: GenerateRequest, db: Session = Depends(get_db)):
    return handle_generate(req, db)

@router.get("/result/{result_id}")
def get_result(result_id: int, db: Session = Depends(get_db)):
    return handle_get_result(result_id, db)