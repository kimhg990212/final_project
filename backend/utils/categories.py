"""
LLM(EXAONE)에 데이터 제공을 위해 상표권 트렌드 분류 카테고리 정의

니스 분류(Nice Classification) 45개 코드를 9개 카테고리로 그룹화.
FR-10 업종별 트렌드 조회에 사용.
"""

CATEGORIES = {
    "패션·잡화": {
        "nice_codes": ["14", "18", "23", "24", "25", "26"],  
    },
    "뷰티·화장품": {
        "nice_codes": ["03"],                               
    },
    "식음료": {
        "nice_codes": ["29", "30", "31", "32", "33", "43"],  
    },
    "IT·전자·통신": {
        "nice_codes": ["09", "38", "42"],                     
    },
    "생활용품·가구": {
        "nice_codes": ["11", "20", "21", "27"],
    },
    "엔터·콘텐츠": {
        "nice_codes": ["15", "16", "28", "41"],
    },
    "헬스·의료": {
        "nice_codes": ["05", "10", "44"],                    
    },
    "교육·서비스·금융": {
        "nice_codes": ["35", "36", "37", "39", "40", "45"],
    },
    "산업·기타": {
        "nice_codes": ["01", "02", "04", "06", "07", "08", "12", "13", "17", "19", "22", "34"],  
    }
}

def get_nice_codes(category_name: str) -> list[str]:
    """카테고리 이름으로 니스 코드 리스트 반환"""
    return CATEGORIES.get(category_name, {}).get("nice_codes", [])


def get_category_by_nice_code(nice_code: str) -> str | None:
    """니스 코드로 소속 카테고리 이름 반환"""
    for category, info in CATEGORIES.items():
        if nice_code in info["nice_codes"]:
            return category
    return None


def get_all_categories() -> list[str]:
    """모든 카테고리 이름 리스트"""
    return list(CATEGORIES.keys())

# 트렌드 분석 단계에서 사용
# KIPRIS 수집 후 LLM 요약 생성 시 "이 상표는 어느 카테고리?" 인지 판별(다중 매칭)
def get_categories_for_trademark(classification_code: str) -> set[str]:
    """
    한 상표의 분류 코드 (| 구분)로 속하는 모든 카테고리 반환
    예: "01|25|26" → {"산업·기타", "패션·잡화"}
        ""        → set() (빈 set)
        None      → set()
    """
    if not classification_code:
        return set()
    
    # | 로 분리
    codes = classification_code.split("|") # ["01", "25", "26"]와 같이 분리
    codes = [c.strip() for c in codes if c.strip()]  # 공백 제거 + 빈 거 제외
    
    categories = set()
    for code in codes:
        cat = get_category_by_nice_code(code)  
        if cat:
            categories.add(cat)
    
    return categories