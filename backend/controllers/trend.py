from services import trend as trend_service

def get_trends(classification: str, period: str, page: int, sort: str):
    return trend_service.get_trends(
        classification=classification,
        period=period,
        page=page,
        sort=sort,
    )

def get_trend_summary(classification: str):  
    return trend_service.get_trend_summary(
        classification=classification
    )    

def get_trend_colors(classification: str):
    return trend_service.get_trend_colors(classification=classification)

def get_trend_classification_stats(classification: str):
    return trend_service.get_trend_classification_stats(
        classification=classification,
    )