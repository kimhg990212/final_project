
from services import trend as trend_service

def get_trends(classification: str, period: str, page: int):
    return trend_service.get_trends(
        classification=classification,
        period=period,
        page=page,
    )