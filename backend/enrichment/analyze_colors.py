import os
import sys
from io import BytesIO
from collections import defaultdict
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from PIL import Image
from sklearn.cluster import KMeans
from sqlalchemy import text
import numpy as np
import requests
from utils.categories import CATEGORIES
from utils.database import engine

# ==============================
# 1. DB에서 이미지 URL 가져오기 
# ==============================
# OCR 길이 기반 필터링 포함
def get_category_image_urls(category_name, nice_codes, period_start, period_end, limit):
    """LLM과 동일 필터 조건으로 big_image_url 가져오기 (도형 중심 로고)"""
    # 로깅용으로 category_name 활용(안 그럼 인자에서 지울 것)
    print(f"  [DB 조회] {category_name} — OCR 필터링 (텍스트 짧은 로고만)") 
    
    like_conditions = " OR ".join([
        f"classification_code LIKE '%{code}%'" 
        for code in nice_codes
    ])
    
    # ocr 필터 조건 : ocr_text IS NULL OR LENGTH(ocr_text) < 10) 
    sql = text(f"""
        SELECT big_image_url
        FROM trademark_trends
        WHERE ({like_conditions})
          AND application_date >= :period_start
          AND application_date <= :period_end
          AND big_image_url IS NOT NULL
          AND big_image_url != ''
          AND (ocr_text IS NULL OR LENGTH(ocr_text) < 10)  
        ORDER BY application_date DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        rows = conn.execute(sql, {
            "period_start": period_start,
            "period_end": period_end,
            "limit": limit
        }).fetchall()
        
    print(f"  [결과] {len(rows)}개 도형 중심 로고 확보") 
    
    return [row.big_image_url for row in rows]


# ==========================
# 2. 이미지 1장에서 색상 추출 
# ==========================
def extract_colors_from_image(image_url, n_colors=5):
    """이미지에서 K-means로 대표 색상 추출 (흰색 배경, 검정색 텍스트 많아 무채색 전체 제외)"""
    try:
       # 다운로드
        response = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        # 크기 축소 (속도)
        img.thumbnail((150, 150))
        
        # 픽셀 배열
        pixels = np.array(img).reshape(-1, 3)

        # R, G, B 추출
        r, g, b = pixels[:, 0], pixels[:, 1], pixels[:, 2]

        # 최대값 - 최소값 = 채도
        max_val = np.maximum(np.maximum(r, g), b)
        min_val = np.minimum(np.minimum(r, g), b)
        saturation = max_val - min_val

        # 채도 30 초과만 통과 (무채색 전체-흰색·검정·회색 모두 제외)
        colorful_mask = saturation > 30
        pixels = pixels[colorful_mask]
        
        # pixels가 채도 필터링으로 줄어들었으니 재선언
        r, g, b = pixels[:, 0], pixels[:, 1], pixels[:, 2]
        # KIPRIS 시스템 공통 파란-회색 패턴 (필터 범위 확장 + 패턴 검증) / 파란-회색 (#7d99bb, #7995b8) 제외
        kipris_blue_mask = ~(
            (r > 100) & (r < 160) &
            (g > 140) & (g < 200) &
            (b > 170) & (b < 240) &
            (b > g) & (g > r)
        )
        pixels = pixels[kipris_blue_mask]
        
        # 표본 부족 처리
        if len(pixels) < n_colors:
            return []
        
        # K-means
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # 색상 + 비율
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        
        result = []
        for i, color in enumerate(colors):
            count = (labels == i).sum()
            percentage = (count / len(labels)) * 100
            hex_color = "#{:02x}{:02x}{:02x}".format(*color)
            result.append({
                "color": hex_color,
                "percentage": percentage
            })
        
        return result
    
    except Exception as e:
        print(f"  ⚠️ 색상 추출 실패: {image_url[:50]}... - {e}")
        return []
    
# =================================
# 3. 카테고리 내 여러 이미지 색상 집계
# =================================
def aggregate_category_colors(image_urls, n_colors=5):
    """여러 이미지의 색상을 집계 → 카테고리 대표 5개 색상"""
    
    color_counter = defaultdict(float)  #  빈 카운터 시작
    success_count = 0
    
    for url in image_urls:
        colors = extract_colors_from_image(url, n_colors)
        if colors:
            success_count += 1
            for c in colors:
                color_counter[c["color"]] += c["percentage"]
    
    # 상위 N개 색상
    top = sorted(color_counter.items(), key=lambda x: x[1], reverse=True)[:n_colors]
    total = sum(v for _, v in top)
    
    return {
        "colors": [
            {"color": c, "percentage": round(v / total * 100, 1)}
            for c, v in top
        ],
        "analyzed_count": success_count
    }

# =============================================
# 4. 9개 카테고리 모두 분석 => 전체 파이프라인 실행   
# =============================================
def analyze_all_categories_colors():
    """전체 카테고리 K-means 색상 분석 실행"""
    
    # LLM 분석 기간과 동일하게 하기 위해 날짜 하드 코딩
    period_start = "20230606"
    period_end = "20260606"
    
    print(f"분석 기간: {period_start} ~ {period_end} (EXAONE과 동일)\n")
    
    results = {}
    for category_name, info in CATEGORIES.items():
        # LLM과 동일 limit
        limit = 120 if category_name == "엔터·콘텐츠" else 140
        
        print(f"[{category_name}] 색상 분석 중... (LIMIT {limit})")
        
        # 1단계: 이미지 URL 가져오기
        image_urls = get_category_image_urls(
            category_name=category_name,
            nice_codes=info["nice_codes"],
            period_start=period_start,
            period_end=period_end,
            limit=limit
        )
        print(f"  → {len(image_urls)}개 이미지 URL 확보")
        
        # 2단계: 색상 집계
        colors = aggregate_category_colors(image_urls)
        results[category_name] = colors
        
        print(f"  ✅ {colors['analyzed_count']}/{len(image_urls)}개 분석 완료")
        print(f"  🎨 대표 색상: {[c['color'] for c in colors['colors']]}")
        print()
    
    # JSON 저장
    output_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "category_colors.json"
    )
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 색상 분석 완료 ===")
    print(f"저장 위치: {output_file}")

# analyze_colors.py 파일이 실행될 때만 analyze_all_categories_colors() 이 함수가 실행되게
if __name__ == "__main__":
    analyze_all_categories_colors()