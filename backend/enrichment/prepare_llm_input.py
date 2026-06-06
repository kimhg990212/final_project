# DB에서 카테고리별 데이터를 LLM 입력 형태로 추출:
# . 9개 카테고리 데이터를 JSON으로 추출
# . 각 카테고리당 최대 500개 상표 (LLM 컨텍스트 한도)
# . Colab에 업로드할 입력 파일임
import os
import sys
import json
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from sqlalchemy import text
from utils.database import engine
from utils.categories import CATEGORIES

# EXAONE 2.4B의 컨택스트 한도 32,768 토큰
def get_category_data(category_name: str, nice_codes: list, 
                      period_start: str, period_end: str, limit: int = 500): # LLM이 한 번에 처리할 수 있는 최대 토큰 수(엑사온 2.4B 컨텍스트 25% 사용)
    """카테고리별 상표 데이터 조회 (LLM 입력용)"""
    
    # 니스 코드 LIKE 조건 만들기
    like_conditions = " OR ".join([
        f"classification_code LIKE '%{code}%'" 
        for code in nice_codes
    ])
    
    sql = text(f"""
        SELECT 
            title, applicant_name, classification_code,
            application_date, ocr_text, caption
        FROM trademark_trends
        WHERE ({like_conditions})
          AND application_date >= :period_start
          AND application_date <= :period_end
        ORDER BY application_date DESC
        LIMIT :limit
    """)
    
    with engine.connect() as conn:
        rows = conn.execute(sql, {
            "period_start": period_start,
            "period_end": period_end,
            "limit": limit
        }).fetchall()
    
    return [
        {
            "title": row.title or "",
            "applicant": row.applicant_name or "",
            "codes": row.classification_code or "",
            "date": row.application_date or "",
            "ocr": row.ocr_text or "",
            "caption": row.caption or ""
        }
        for row in rows
    ]

def main():
    """모든 카테고리의 LLM 입력 데이터 생성"""
    today = date.today()
    three_years_ago = today.replace(year=today.year - 3)
    
    period_start = three_years_ago.strftime("%Y%m%d")  
    period_end = today.strftime("%Y%m%d")             
    
    print(f"기간: {period_start} ~ {period_end}\n")
    
    output = {}
    
    for category_name, info in CATEGORIES.items():
        print(f"[{category_name}] 데이터 추출 중...")
        
        data = get_category_data(
            category_name=category_name,
            nice_codes=info["nice_codes"],
            period_start=period_start,
            period_end=period_end,
            limit=500      
        )
        
        output[category_name] = {
            "nice_codes": info["nice_codes"],
            "period_start": period_start,
            "period_end": period_end,
            "trademark_count": len(data),
            "trademarks": data
        }
        
        print(f"  → {len(data)}개 추출")
    
    # JSON 저장
    output_file = "llm_input_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 완료: {output_file} ===")
    print(f"카테고리 9개, 카테고리당 최대 500개 상표")


if __name__ == "__main__":
    main()
