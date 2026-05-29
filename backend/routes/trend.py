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


