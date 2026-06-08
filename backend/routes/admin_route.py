from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from utils.database import get_db
from models.user import User
from models.kipris_trademark import KiprisTrademark

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/trademarks")
def get_admin_trademarks(
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=100),
    keyword: str | None = None,
    sort: str = "latest",
    db: Session = Depends(get_db),
):
    query = db.query(KiprisTrademark)

    if keyword:
        query = query.filter(
            or_(
                KiprisTrademark.title.like(f"%{keyword}%"),
                KiprisTrademark.applicant_name.like(f"%{keyword}%"),
                KiprisTrademark.application_number.like(f"%{keyword}%"),
            )
        )

    if sort == "oldest":
        query = query.order_by(asc(KiprisTrademark.application_date))
    else:
        query = query.order_by(desc(KiprisTrademark.application_date))

    total = query.count()

    items = (
        query
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": items,
    }


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
    
    
@router.delete("/trademarks/{trademark_id}")
def delete_trademark(trademark_id: int, db: Session = Depends(get_db)):
    trademark = db.query(KiprisTrademark).filter(
        KiprisTrademark.id == trademark_id
    ).first()

    if not trademark:
        raise HTTPException(status_code=404, detail="상표를 찾을 수 없습니다.")

    db.delete(trademark)
    db.commit()

    return {"message": "상표가 삭제되었습니다."}