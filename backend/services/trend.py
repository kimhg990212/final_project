from datetime import datetime, timedelta
from models import trend
from utils.database import engine


def get_trends(classification, period, page, size=20):
    """
    트렌드 조회 — controllers에서 받은 값을 DB 쿼리용으로 변환 후 실행
    
    classification: 업종(니스) 코드 (빈 문자열·None이면 전체)
    period:         기간 (년 단위, 예: 1, 3)
    page:           페이지 번호 (1부터 시작)
    size:           페이지당 건수 (기본 20)
    """
    # 1. period → start_date 계산 (오늘에서 N년 전)
    days_map = {"6m": 180, "1y": 365, "3y": 365 * 3}
    days = days_map[period]
    today = datetime.now()
    start = today - timedelta(days=days)  # 앞 days는 timedelta가 요구하는 파라미터/뒤의 days는 days_map[period]
    start_date = start.strftime("%Y%m%d")

    # 2. page → offset 계산
    offset = (page - 1) * size

    # 3. DB 조회 (목록 + 총 건수)
    with engine.connect() as conn:
        rows  = trend.get_trends_query(conn, classification, start_date, size, offset)
        total = trend.count_trends_query(conn, classification, start_date)

    # 4. SQLAlchemy 행을 dict 리스트로 변환 (JSON으로 보낼 수 있게)
    data = [dict(row._mapping) for row in rows]

    # 5. 응답 형태로 묶어서 controllers에게 반환
    return {
        "data":  data,    # 트렌드 상표들(20개)
        "total": total,   # 전체 건수 (예: 1234)
        "page":  page,    # 현재 페이지
        "size":  size,    # 페이지당 개수
    }