from utils.text_utils import extract_text_from_file
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def generate_from_file_task(file_path: str, prompt: str, result_id: int):

    from utils.database import SessionLocal
    from models.result_model import GeneratedResult

    db = SessionLocal()

    try:
        extracted_text = extract_text_from_file(file_path)

        if not extracted_text:
            raise ValueError("파일에서 텍스트를 추출할 수 없습니다.")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "주어진 문서를 바탕으로 사용자의 요청에 응답해주세요."},
                {"role": "user", "content": f"[문서 내용]\n{extracted_text}\n\n[요청]\n{prompt}"}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        result_text = response.choices[0].message.content

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