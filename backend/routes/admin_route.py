from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from utils.database import get_db
from models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "role": user.role,
            "is_deleted": user.is_deleted,
            "created_at": user.created_at
        }
        for user in users
    ]


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"message": "사용자를 찾을 수 없습니다."}

    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "role": user.role,
        "is_deleted": user.is_deleted,
        "created_at": user.created_at
    }