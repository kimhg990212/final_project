from fastapi import APIRouter, Form
from controllers.search_controller import (
    get_categories_controller,
    search_logo_controller
)

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

# 카테고리 목록 반환 (드롭다운용)
@router.get("/categories")
def get_categories():
    return get_categories_controller()

# 비유사 TOP3 로고 조회
@router.post("/logo")
async def search_logo(
    category_name: str = Form(...),
    brand_description: str = Form(...),
    style: str = Form(default="")
):
    return await search_logo_controller(
        category_name=category_name,
        brand_description=brand_description,
        style=style
    )