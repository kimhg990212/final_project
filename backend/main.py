import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.routes import plagiarism_route

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
    
    logger.info("================================================")
    logger.info("AI 기반 상표 도용 탐지 백엔드 시스템 (MVP 호스팅 시작)")
    logger.info("담당 기능: FR-01(탐지), FR-02(출력 시각화), FR-04(근거설명)")
    logger.info("================================================")
    
    yield
    
    logger.info("AI 도용 탐지 시스템 서버를 종료합니다.")

app = FastAPI(
    title="AI기반 상표/로고 도용 탐지 시스템 API",
    description="CLIP 임베딩 및 FAISS 백터 스토리지를 활용한 실시간 도용 매칭 백엔드 엔진",
    version="1.0.0",
    lifespan=lifespan
)

# React 프론트엔드 연동을 위한 CORS 정책 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP 단계이므로 전역 허용 (배포 시 프론트 주소로 한정)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 도용 탐지 핵심 라우터 등록
app.include_router(plagiarism_route.router)

@app.get("/health", tags=["인프라 체크"])
async def health_check():
    """서버 헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "plagiarism-detection-api"}