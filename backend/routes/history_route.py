from fastapi import APIRouter

router = APIRouter(
    prefix="/history",
    tags=["History"]
)

@router.get("/my")

def get_my_history():

    return {
        "message": "생성 이력 조회"
    }