import os
from typing import Callable

import requests
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from models.user import User
from utils.database import get_db

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
google_bearer_scheme = HTTPBearer(auto_error=False)


def verify_google_id_token(id_token: str) -> dict:
    try:
        response = requests.get(
            GOOGLE_TOKENINFO_URL,
            params={"id_token": id_token},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=503,
            detail="Google 토큰 검증에 실패했습니다.",
        ) from exc

    if not response.ok:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 Google 토큰입니다.",
        )

    token_info = response.json()
    expected_client_id = os.getenv("GOOGLE_CLIENT_ID")

    if expected_client_id and token_info.get("aud") != expected_client_id:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 Google 토큰입니다.",
        )

    issuer = token_info.get("iss")
    if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 Google 토큰입니다.",
        )

    return token_info


def require_google_user(admin_only: bool = False) -> Callable:
    def _require_google_user(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Security(google_bearer_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=401,
                detail="인증 정보가 없습니다.",
            )

        token_info = verify_google_id_token(credentials.credentials)
        google_sub = token_info.get("sub")
        if not google_sub:
            raise HTTPException(
                status_code=401,
                detail="유효하지 않은 Google 토큰입니다.",
            )

        user = db.query(User).filter(User.google_sub == google_sub).first()
        if not user or user.is_deleted:
            raise HTTPException(
                status_code=401,
                detail="등록되지 않은 사용자입니다.",
            )

        if admin_only and user.role != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="관리자 권한이 필요합니다.",
            )

        request.state.current_user = user

        return user

    return _require_google_user
