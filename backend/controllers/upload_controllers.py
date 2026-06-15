# 비즈니스 로직 처리 하는 기능
# route에서 받은 요청을 처리
from fastapi import UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from services.file_service import save_upload_file
from services.ai_service import generate_from_file_task
from models.file_model import UploadedFile
from models.result_model import GeneratedResult
from schemas.upload_schema import GenerateRequest

# 파일 저장 + DB에 파일 정보 기록
async def handle_upload(file: UploadFile, db: Session):
    file_info = await save_upload_file(file)
    
    db_file = UploadedFile(**file_info)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

# DB에 결과 레코드 생성후 BackgroundTasks로 AI생성 등록
async def handle_generate(req: GenerateRequest, db: Session, background_tasks: BackgroundTasks):
    db_file = db.query(UploadedFile).filter(
        UploadedFile.id == req.file_id
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    db_result = GeneratedResult(
        file_id=req.file_id,
        prompt=req.prompt,
        result_image="처리 중..."
    )
    try:
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        background_tasks.add_task(generate_from_file_task, db_file.saved_path, req.prompt, db_result.id)
        return db_result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="처리 중 오류가 발생했습니다.")

# DB에서 결과 조회해서 반환
def handle_get_result(result_id: int, db: Session):
    result = db.query(GeneratedResult).filter(
        GeneratedResult.id == result_id
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")
    return result