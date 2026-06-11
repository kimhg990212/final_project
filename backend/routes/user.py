from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
  
from utils.database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin
from utils.auth import hash_password, verify_password

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
    
@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    return {
        "message": "로그인 성공",
        "user_id": db_user.id,
        "email": db_user.email,
        "nickname": db_user.nickname,
        "role": db_user.role
    }
    
@router.post("/logout")
def logout():
    return {
        "message": "로그아웃 성공"
    }
    
@router.delete("/withdraw/{user_id}")
def withdraw(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="사용자를 찾을 수 없습니다."
        )

    user.is_deleted = True

    db.commit()

    return {
        "message": "회원탈퇴 완료"
    }
    