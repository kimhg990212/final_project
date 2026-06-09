from pydantic import BaseModel

class GenerateRequest(BaseModel):
    file_id: int
    prompt: str