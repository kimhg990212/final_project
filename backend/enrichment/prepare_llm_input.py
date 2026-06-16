# DB에서 카테고리별 데이터를 LLM 입력 형태로 추출

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from sqlalchemy import text
from utils.database import engine
from utils.categories import CATEGORIES

# EXAONE 2.4B의 컨택스트 한도: 32,768 토큰
def get_category_data(category_name: str, nice_codes: list, 
                      period_start: str, period_end: str, limit: int = 500): # LLM이 한 번에 처리할 수 있는 최대 토큰 수(예상)
    """카테고리별 상표 데이터 조회 (LLM 입력용)"""
    
    like_conditions = " OR ".join([
        f"classification_code LIKE '%{code}%'" 
        for code in nice_codes
    ])
    
    sql = text(f"""
        SELECT 
            title, applicant_name, classification_code,
            application_date, ocr_text, caption
        FROM kipris_trademarks
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

# 니스 코드별로 건수 집계 (차트 방식처럼 코드별 건수를 계산해서, 같은 숫자를 EXAONE한테도 넘김 → 할루시네이션 방지)
def get_code_counts(nice_codes, period_start, period_end):
    """니스 코드별 출원 건수 — 차트(get_classification_stats_query)와 동일 기준"""
    counts = []
    with engine.connect() as conn:
        for code in nice_codes:
            cnt = conn.execute(text("""
                SELECT COUNT(*) FROM kipris_trademarks
                WHERE classification_code LIKE :pattern
                  AND application_date >= :ps
                  AND application_date <= :pe
            """), {"pattern": f"%{code}%", "ps": period_start, "pe": period_end}).scalar()
            counts.append({"code": code, "count": int(cnt or 0)})
    counts.sort(key=lambda x: x["count"], reverse=True)
    return counts

# main()에서 기간을 차트와 동일하게 고정 + code_counts 포함
def main():
    period_start = "20230606"
    period_end   = "20260606"
    print(f"기간: {period_start} ~ {period_end}\n")

    output = {}
    for category_name, info in CATEGORIES.items():
        print(f"[{category_name}] 데이터 추출 중...")
        
        # DB에서 데이터 가져옴
        data = get_category_data(
            category_name, info["nice_codes"],
            period_start, period_end, limit=500, # 카테고리당 최대 500개 (LLM 컨텍스트 한도 고려)
        )
        code_counts = get_code_counts(info["nice_codes"], period_start, period_end)  
        # output에 추가
        output[category_name] = {
            "nice_codes": info["nice_codes"],
            "period_start": period_start,
            "period_end": period_end,
            "trademark_count": len(data),
            "code_counts": code_counts,   # 차트와 같은 코드별 건수
            "trademarks": data,
        }
        print(f"  → 상표 {len(data)}개 추출, 코드 {len(code_counts)}종 집계")
     
    with open("llm_input_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print("\n=== 완료: llm_input_data.json ===")  
    print(f"카테고리 9개, 카테고리당 최대 500개 상표")

if __name__ == "__main__":
    main()
