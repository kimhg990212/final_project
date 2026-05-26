def extract_keywords(user_text:str):
    text = user_text.lower()
    
    keywords ={
        "category":"logo",
        "style":"auto",
        "color":[],
        "mood":[],
        "complexity":"balanced",
        "logo_type":"auto",
        "raw_text":user_text
    }
    
    color_map = {
        "브라운": "brown",
        "갈색": "brown",
        "레드": "red",
        "빨강": "red",
        "골드": "gold",
        "금색": "gold",
        "블랙": "black",
        "검정": "black",
        "화이트": "white",
        "흰색": "white"
    }

    mood_map = {
        "따뜻": "warm",
        "고급": "luxury",
        "엘레강스": "elegant",
        "우아": "elegant",
        "감성": "emotional",
        "귀여": "cute",
        "깔끔": "clean"
    }

    style_map = {
        "미니멀": "minimal",
        "심플": "minimal",
        "빈티지": "vintage",
        "클래식": "classic",
        "모던": "modern"
    }

    complexity_map = {
        "simple": ["단순", "심플", "미니멀", "깔끔"],
        "ornate": ["화려", "장식", "고급", "엘레강스", "클래식", "빈티지"]
    }

    logo_type_map = {
        "emblem": ["엠블럼", "배지", "뱃지", "테두리", "원형"],
        "text": ["글자", "텍스트", "타이포"],
        "symbol_text": ["아이콘", "심볼", "그림"]
    }

    for kor, eng in color_map.items():
        if kor in user_text:
            keywords["color"].append(eng)

    for kor, eng in mood_map.items():
        if kor in user_text:
            keywords["mood"].append(eng)

    for kor, eng in style_map.items():
        if kor in user_text:
            keywords["style"] = eng

    for level, words in complexity_map.items():
        if any(word in user_text for word in words):
            keywords["complexity"] = level

    for logo_type, words in logo_type_map.items():
        if any(word in user_text for word in words):
            keywords["logo_type"] = logo_type

    if "카페" in user_text:
        keywords["category"] = "cafe"
    elif "밀크티" in user_text:
        keywords["category"] = "milk tea cafe"
    elif "식당" in user_text or "음식점" in user_text:
        keywords["category"] = "restaurant"

    if not keywords["color"]:
        keywords["color"] = ["auto"]

    if not keywords["mood"]:
        keywords["mood"] = ["auto"]

    return keywords