import json
import os
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from models import trend
from utils.database import engine
from utils.categories import get_category_by_nice_code, get_nice_codes


# "latest": 최신 출원일
def get_trends(classification, period, page, sort="latest", size=20):
    """
    트렌드 조회 — controllers에서 받은 값을 DB 쿼리용으로 변환 후 실행

    classification: 업종(니스) 코드 (빈 문자열·None이면 전체)
    period:         기간 ("6m" | "1y" | "3y")               
    page:           페이지 번호 (1부터 시작)
    sort:           정렬 기준 ("latest" | "oldest" | "applicant", 기본 "latest")   
    size:           페이지당 건수 (기본 20)
    """
    
    # 1. period → start_date 계산 (차트·요약과 동일 기준 / 데이터를 지속 적재하지 않는 상황이다 보니 차트·요약과 동일 기준으로 기준일 2026-06-06으로 고정)
    months_map = {"6m": 6, "1y": 12, "3y": 36}
    today = datetime(2026, 6, 6) # datetime.now() 대신 고정
    start = today - relativedelta(months=months_map[period])
    start_date = start.strftime("%Y%m%d")

    # 2. page → offset 계산
    offset = (page - 1) * size

    # 3. DB 조회 (목록 + 총 건수)
    with engine.connect() as conn:
        rows  = trend.get_trends_query(conn, classification, start_date, sort, size, offset)
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
    
def get_trend_summary(classification):
    """
    트렌드 요약 조회 — 카테고리 단위 LLM 요약 반환
    
    classification: 업종(니스) 코드 (빈 문자열·None이면 None 반환)
    """
    # 1. 전체 선택(빈 문자열)이면 즉시 None 반환
    if not classification:
        return None
    
    # 2. DB 조회
    with engine.connect() as conn:
        row = trend.get_summary_query(conn, classification)
    
    # 3. 결과 없으면 None
    if not row:
        return None
    
    # 4. SQLAlchemy 행을 dict로 변환    
    # 문자열로 반환되다 보니 배열 변환을 위해 dict로 변환 후 data에 담음
    data = dict(row._mapping)  
    if data.get("keywords") and isinstance(data["keywords"], str):
        try:
            data["keywords"] = json.loads(data["keywords"])
            #        ↑                            ↑
            #   딕셔너리의 한 키            그 키의 현재 값(문자열)
        except json.JSONDecodeError:
            data["keywords"] = []
    
    return data   # 딕셔너리 반환 (FastAPI가 자동으로 JSON 객체로 변환해서 응답)

# 컬러 분석 api
def get_trend_colors(classification: str):
    if not classification:
        return None   # 빈 값일 때 처리
    
    # 1. category_name 매핑 (만들어둔 utils. get_category_by_nice_code 함수 사용)
    category_name = get_category_by_nice_code(classification)
    if not category_name:
        return None      # 매핑 실패 시
    
    # 2. JSON 파일 경로 
    json_path = os.path.join(
        os.path.dirname(__file__),
        "..", "enrichment", "category_colors.json"
    )
    
    # 3. 파일 존재 체크
    if not os.path.exists(json_path):
        return None
    
    # 4. json 로드 + 반환
    with open(json_path, "r", encoding="utf-8") as f:
        all_colors = json.load(f)
    
    # 카테고리 데이터 추출
    category_data = all_colors.get(category_name)
    if not category_data:
        return None
    
    # 6. 응답 형식(명시적 반환 형식)
    return {
        "category": category_name,
        "colors": category_data.get("colors", []),
        "analyzed_count": category_data.get("analyzed_count", 0)
    }

# 카테고리 그룹 내 어떤 니스 코드가 많이 출원됐는지 시각화  
def get_trend_classification_stats(classification):
    """카테고리 그룹 내 분류 코드별 빈도 + 한글 라벨"""
    if not classification:
        return None
    
    # 1. 카테고리 매핑
    category_name = get_category_by_nice_code(classification)
    if not category_name:
        return None
    
    # 2. 카테고리에 속한 니스 코드들
    nice_codes = get_nice_codes(category_name)
    
    # 3. DB 조회
    with engine.connect() as conn:
        stats = trend.get_classification_stats_query(conn, nice_codes)
    
    # 4. 한글 라벨 + 비율 계산
    total = sum(s["count"] for s in stats)
    
    # "현재는 빠른 개발을 우선시했고, 
    # 향후 utils/categories.py로 중앙화하여 단일 출처(SSOT)로 관리 예정
    NICE_LABELS = {
    "01": "공업용 화학제품", 
    "02": "페인트, 도료",           
    "03": "세제, 화장품",           
    "04": "공업용 오일, 양초",       
    "05": "약제, 의료용 제제",      
    "06": "금속, 광석",             
    "07": "기계", 
    "08": "수공구", 
    "09": "전자기기, 컴퓨터",       
    "10": "의료기기", 
    "11": "조명, 가전",             
    "12": "운송장치",
    "13": "화기, 폭약",          
    "14": "보석, 시계",            
    "15": "악기",
    "16": "종이, 인쇄물, 문구",     
    "17": "고무, 플라스틱",        
    "18": "가죽, 가방",            
    "19": "비금속 건축재료", 
    "20": "가구", 
    "21": "가정용품",
    "22": "로프, 그물",             
    "23": "실, 사",                
    "24": "직물",
    "25": "의류, 신발, 모자",      
    "26": "레이스, 단추",           
    "27": "카펫, 매트",             
    "28": "완구, 운동용품",         
    "29": "식육, 가공식품",         
    "30": "곡물, 빵, 차, 커피",     
    "31": "농축산물, 종자",        
    "32": "맥주, 음료",             
    "33": "알코올 음료", 
    "34": "담배", 
    "35": "광고, 사업관리",        
    "36": "금융, 보험, 부동산",     
    "37": "건설, 수리",             
    "38": "통신", 
    "39": "운수, 보관, 여행",      
    "40": "재료처리, 재생",         
    "41": "교육, 오락, 스포츠",     
    "42": "과학기술, IT 디자인",    
    "43": "음식점, 숙박",           
    "44": "의료, 미용, 농업",       
    "45": "법률, 보안, 기타 서비스", 
    }
    
    data = sorted(
        [
            {
                "code": s["code"],
                "label": f"{s['code']}번 ({NICE_LABELS.get(s['code'], s['code'])})",
                "count": s["count"],
                "percentage": round(s["count"] / total * 100, 1) if total > 0 else 0
            }
            for s in stats 
        ],
        key=lambda x: x["count"],
        reverse=True
    )
    
    return {
        "category": category_name,
        "data": data,
        "total": total
    }
