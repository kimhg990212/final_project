def extract_keywords(user_text: str):
    text = user_text.lower()

    keywords = {
        "category": "logo",
        "business_type": "general",
        "style": "auto",
        "color": [],
        "mood": [],
        "complexity": "balanced",
        "logo_type": "auto",
        "raw_text": user_text
    }

    business_type_map = {
        "cafe": ["카페", "커피", "디저트", "베이커리"],
        "restaurant": ["식당", "음식점", "레스토랑", "분식", "한식", "양식", "중식", "일식"],
        "beauty": ["뷰티", "미용", "네일", "헤어", "화장품", "피부"],
        "fashion": ["패션", "의류", "옷", "쇼핑몰", "브랜드"],
        "education": ["학원", "교육", "과외", "스터디", "학교"],
        "medical": ["병원", "의원", "치과", "한의원", "약국"],
        "fitness": ["헬스", "운동", "피트니스", "요가", "필라테스", "pt"],
        "tech": ["IT", "앱", "소프트웨어", "개발", "AI", "플랫폼", "스타트업"],
        "pet": ["반려동물", "펫", "강아지", "고양이", "애견"],
        "real_estate": ["부동산", "공인중개사", "건물", "인테리어"],
        "law": ["법률", "변호사", "로펌"],
        "flower": ["꽃집", "플라워", "꽃"],
        "milk_tea_cafe": ["밀크티"]
    }

    color_map = {
        "브라운": "brown", "갈색": "brown",
        "레드": "red", "빨강": "red",
        "골드": "gold", "금색": "gold",
        "블랙": "black", "검정": "black",
        "화이트": "white", "흰색": "white",
        "핑크": "pink", "분홍": "pink",
        "블루": "blue", "파랑": "blue","푸른": "blue",
        "그린": "green", "초록": "green",
        "옐로우": "yellow", "노랑": "yellow",
        "퍼플": "purple", "보라": "purple",
        "오렌지": "orange", "주황": "orange"
    }

    mood_map = {
        "따뜻": "warm",
        "고급": "luxury",
        "엘레강스": "elegant",
        "우아": "elegant",
        "감성": "emotional",
        "귀여": "cute",
        "깔끔": "clean",
        "전문": "professional",
        "신뢰": "trustworthy",
        "활기": "energetic",
        "차분": "calm",
        "힙": "trendy"
    }

    style_map = {
        "미니멀": "minimal",
        "심플": "minimal",
        "빈티지": "vintage",
        "클래식": "classic",
        "모던": "modern",
        "레트로": "retro",
        "럭셔리": "luxury",
        "고급": "luxury",
        "귀여": "cute",
        "캐주얼": "casual"
    }

    complexity_map = {
        "simple": ["단순", "심플", "미니멀", "깔끔"],
        "ornate": ["화려", "장식", "고급", "엘레강스", "클래식", "빈티지"]
    }

    logo_type_map = {
        "emblem": ["엠블럼", "배지", "뱃지", "테두리", "원형"],
        "text": ["글자", "텍스트", "타이포", "워드마크"],
        "symbol_text": ["아이콘", "심볼", "그림", "마스코트"]
    }

    for business_type, words in business_type_map.items():
        if any(word.lower() in text for word in words):
            keywords["business_type"] = business_type
            break

    for kor, eng in color_map.items():
        if kor.lower() in text:
            keywords["color"].append(eng)

    for kor, eng in mood_map.items():
        if kor.lower() in text:
            keywords["mood"].append(eng)

    for kor, eng in style_map.items():
        if kor.lower() in text:
            keywords["style"] = eng

    for level, words in complexity_map.items():
        if any(word.lower() in text for word in words):
            keywords["complexity"] = level

    for logo_type, words in logo_type_map.items():
        if any(word.lower() in text for word in words):
            keywords["logo_type"] = logo_type

    if not keywords["color"]:
        keywords["color"] = ["auto"]

    if not keywords["mood"]:
        keywords["mood"] = ["auto"]

    return keywords