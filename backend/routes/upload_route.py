# 업로드 기능의 시작점
# 클라이언트 요청을 받는 엔드포인트
from fastapi import APIRouter, UploadFile,BackgroundTasks, File, Depends
from sqlalchemy.orm import Session
from utils.database import get_db
from controllers.upload_controllers import (
    handle_upload,
    handle_generate,
    handle_get_result
)
from schemas.upload_schema import GenerateRequest

router = APIRouter(prefix="/Upload", tags=["Upload"])

# 파일 업로드 요청 받음
@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await handle_upload(file, db)

# AI 생성 요청 받음
@router.post("/generate")
async def generate_content(req: GenerateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    return await handle_generate(req, db, background_tasks)

# 결과 조회 요청 받음
@router.get("/result/{result_id}")
def get_result(result_id: int, db: Session = Depends(get_db)):
    return handle_get_result(result_id, db)