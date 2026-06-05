from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from services.file_service import save_upload_file
from services.ai_service import generate_from_file_task
from models.file_model import UploadedFile
from models.result_model import GeneratedResult
from utils.response_utils import GenerateRequest

async def handle_upload(file: UploadFile, db: Session):
    file_info = await save_upload_file(file)
    
    db_file = UploadedFile(**file_info)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def handle_generate(req: GenerateRequest, db: Session):
    db_file = db.query(UploadedFile).filter(
        UploadedFile.id == req.file_id
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    db_result = GeneratedResult(
        file_id=req.file_id,
        prompt=req.prompt,
        result_text="처리 중..."
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    generate_from_file_task.delay(db_file.saved_path, req.prompt, db_result.id)
    return db_result

def handle_get_result(result_id: int, db: Session):
    result = db.query(GeneratedResult).filter(
        GeneratedResult.id == result_id
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")
    return result