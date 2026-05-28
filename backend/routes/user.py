from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from utils.database import get_db
from models.user import User
from schemas.user import UserCreate
from utils.auth import hash_password

router = APIRouter()

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    # 이메일 중복 검사
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="이미 존재하는 이메일입니다."
        )

    # 비밀번호 암호화
    hashed_pw = hash_password(user.password)

    # User 객체 생성
    new_user = User(
        email=user.email,
        password=hashed_pw,
        nickname=user.nickname
    )

    # DB 저장
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "회원가입 성공",
        "user_id": new_user.id
    }