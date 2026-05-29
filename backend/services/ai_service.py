from utils.text_utils import extract_text_from_file

def generate_from_file_task(file_path: str, prompt: str, result_id: int):
    
    from utils.database import SessionLocal
    from models.result_model import GeneratedResult
    
    db = SessionLocal()
    
    try:
        # 파일에서 텍스트 추출 (utils/text_utils.py 활용)
        extracted_text = extract_text_from_file(file_path)
        
        if not extracted_text:
            raise ValueError("파일에서 텍스트를 추출할 수 없습니다.")
        
        result_text = extracted_text  
        
        # 데이터베이스에 최종 결과 업데이트
        db.query(GeneratedResult).filter(
            GeneratedResult.id == result_id
        ).update({"result_text": result_text})
        db.commit()
        
        return result_text
    
    except Exception as e:
        db.rollback() 
        
        db.query(GeneratedResult).filter(
            GeneratedResult.id == result_id
        ).update({"result_text": f"오류 발생: {str(e)}"})
        db.commit()
        raise e
    
    finally:
    
        db.close()