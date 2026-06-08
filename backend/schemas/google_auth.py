from pydantic import BaseModel


class GoogleLoginRequest(BaseModel):
    token: str


class GoogleProfileUpdateRequest(BaseModel):
    email: str
    nickname: str
