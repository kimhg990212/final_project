
from fastapi import APIRouter, Query
from typing import Literal
from controllers import trend as trend_controller

router = APIRouter()

@router.get("")   
def get_trends(
    classification: str = Query(""),
    period: Literal["6m", "1y", "3y"] = Query("1y"),
    page: int = Query(1, ge=1),               # ge=1은 "1 이상"
    sort: Literal["latest", "oldest", "applicant"] = Query("latest"),
):
    return trend_controller.get_trends(
        classification=classification,
        period=period,
        page=page,
        sort=sort,
    )
    
@router.get("/summary")
def get_trend_summary(
    classification: str = Query(""),   
):
    return trend_controller.get_trend_summary(
        classification=classification,       
    )

@router.get("/colors")
def get_trend_colors(classification: str = Query("")):
    return trend_controller.get_trend_colors(classification=classification)

# 카테고리 그룹 내 어떤 니스 코드가 많이 출원됐는지 시각화 위해
@router.get("/classification-stats")
def get_trend_classification_stats(classification: str = Query("")):
    return trend_controller.get_trend_classification_stats(
        classification=classification,
    )  