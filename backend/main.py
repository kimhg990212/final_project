import uvicorn, os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routes import post, text_logo, trend, user, admin_route

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

if __name__ == "__main__":
    uvicorn.run(
        "main:app",          # 모듈:앱 경로
        host=os.getenv("HOST"), 
        port=int(os.getenv("PORT")),
        reload=True,
    )
