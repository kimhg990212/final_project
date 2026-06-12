# 요청 데이터 검증
from pydantic import BaseModel

# GenerateRequest — /generate 요청 시 file_id(int)와 prompt(str) 필수 검증
class GenerateRequest(BaseModel):
    file_id: int
    prompt: str