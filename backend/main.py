import uvicorn, os
import logging
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from routes import post, text_logo, trend, user, admin_route, plagiarism_route, google_auth

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작 및 종료 시 안전하게 리소스를 확보하는 Lifespan 이벤트"""
    # 1. 파일 업로드 디렉토리 자동 빌드 체크
    upload_path = "./uploads/images"
    if not os.path.exists(upload_path):
        os.makedirs(upload_path, exist_ok=True)
        logger.info(f"업로드 디렉토리 생성 완료: {upload_path}")
    
    yield
    
    logger.info("AI 도용 탐지 시스템 서버를 종료합니다.")

app = FastAPI(
    title="AI기반 상표/로고 도용 탐지 및 로고 생성 시스템 API",
    description="CLIP 임베딩 및 FAISS 백터 스토리지를 활용한 실시간 도용 매칭 백엔드 엔진",
    version="1.0.0",
    lifespan=lifespan
)
app.mount(
    "/uploads/images",
    StaticFiles(directory="uploads/images"),
    name="uploads_images"
)

# React 프론트엔드 연동을 위한 CORS 정책 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP 단계이므로 전역 허용 (배포 시 프론트 주소로 한정)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 도용 탐지 기능 추가 라우터(도용 탐지 -> 결과 및 리포트 출력)
app.include_router(plagiarism_route.router)

# FR-05기능 추가 라우터 (자연어 -> 이미지 생성 기능)
app.include_router(text_logo.router)

# FR-19기능 추가 라우터 (관리자- 사용자 목록 조회 기능)
app.include_router(admin_route.router)

# FR-08기능 추가 라우터
# from routes.generate_route import (
#     router as generate_router
# )

# from middleware.error_middleware import (
#     global_exception_handler
# )
# app.include_router(generate_router)

# app.add_exception_handler(
#     Exception,
#     global_exception_handler
# )

@app.get("/")
def root():

    return {
        "message": "Server Running"
    }

#FR-09기능 추가 라우터 
# from routes.search_route import (
#     router as search_router
# )

# app.include_router(
#     search_router
# )


app.include_router(trend.router, prefix="/trends")

app.include_router(post.router, prefix="/posts")

app.include_router(user.router, prefix= "/users")
app.include_router(google_auth.router, prefix="/users/google")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",          # 모듈:앱 경로
        host=os.getenv("HOST"), 
        port=int(os.getenv("PORT")),
        reload=True,
    )
