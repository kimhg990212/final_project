from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from models.user import User
from schemas.google_auth import GoogleLoginRequest, GoogleProfileUpdateRequest
from utils.database import get_db
from utils.google_auth import verify_google_id_token


def google_login_controller(
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db),
) -> dict:
    token_info = verify_google_id_token(payload.token)

    google_sub = token_info.get("sub")
    email = token_info.get("email")
    name = token_info.get("name") or token_info.get("given_name")

    if not google_sub or not email or not name:
        raise HTTPException(
            status_code=400,
            detail="Google 계정 정보가 올바르지 않습니다.",
        )

    user = db.query(User).filter(User.google_sub == google_sub).first()

    if not user:
        user = db.query(User).filter(User.email == email).first()

    if user:
        user.google_sub = google_sub
    else:
        user = User(
            google_sub=google_sub,
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
        "google_sub": user.google_sub,
        "email": user.email,
        "nickname": user.nickname,
        "role": user.role,
    }


def read_google_me_controller(request: Request):
    return build_google_user_response(request.state.current_user)


def read_google_admin_me_controller(request: Request):
    return build_google_user_response(request.state.current_user)


def update_google_me_controller(
    payload: GoogleProfileUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = request.state.current_user

    email = payload.email.strip()
    nickname = payload.nickname.strip()

    if not email or not nickname:
        raise HTTPException(
            status_code=400,
            detail="닉네임과 이메일을 모두 입력해주세요.",
        )

    existing_user = (
        db.query(User)
        .filter(User.email == email, User.id != current_user.id)
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="이미 사용 중인 이메일입니다.",
        )

    current_user.email = email
    current_user.nickname = nickname
    db.commit()
    db.refresh(current_user)

    return {
        "message": "개인정보가 수정되었습니다.",
        **build_google_user_response(current_user),
    }
