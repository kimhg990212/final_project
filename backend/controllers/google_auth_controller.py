from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from models.user import User
from schemas.google_auth import GoogleLoginRequest
from utils.database import get_db
from utils.google_auth import verify_google_id_token


def google_login_controller(
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db),
) -> dict:
    token_info = verify_google_id_token(payload.token)

    email = token_info.get("email")
    name = token_info.get("name") or token_info.get("given_name")

    if not email or not name:
        raise HTTPException(
            status_code=400,
            detail="Google 계정 정보가 올바르지 않습니다.",
        )

    user = db.query(User).filter(User.email == email).first()

    if user:
        user.nickname = name
    else:
        user = User(
            email=email,
            nickname=name,
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    return {
        "message": "Google 로그인 성공",
        **build_google_user_response(user),
    }


def build_google_user_response(user: User) -> dict:
    return {
        "user_id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "role": user.role,
    }


def read_google_me_controller(request: Request):
    return build_google_user_response(request.state.current_user)


def read_google_admin_me_controller(request: Request):
    return build_google_user_response(request.state.current_user)
