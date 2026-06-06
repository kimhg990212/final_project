# Colab 결과를 DB에 적재

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from sqlalchemy import text
from utils.database import engine


def main():
    """Colab 결과 JSON을 trend_summaries 테이블에 적재"""
    
    input_file = "llm_output_summaries.json"
    
    with open(input_file, "r", encoding="utf-8") as f:
        summaries = json.load(f)
    
    print(f"{len(summaries)}개 요약 적재 시작...\n")
    
    sql = text("""
        INSERT INTO trend_summaries (
            category_name, nice_codes, summary_text, keywords,
            trademark_count, period_start, period_end, model_name, generated_at
        )
        VALUES (
            :category_name, :nice_codes, :summary_text, :keywords,
            :trademark_count, :period_start, :period_end, :model_name, :generated_at
        )
        ON DUPLICATE KEY UPDATE
            summary_text = VALUES(summary_text),
            keywords = VALUES(keywords),
            trademark_count = VALUES(trademark_count),
            model_name = VALUES(model_name),
            generated_at = VALUES(generated_at)
    """)
    
    with engine.begin() as conn:
        for category_name, data in summaries.items():
            # nice_codes 리스트 → 콤마 구분 문자열
            nice_codes_str = ",".join(data["nice_codes"])
            
            # keywords 리스트 → JSON 문자열
            keywords_json = json.dumps(data.get("keywords", []), ensure_ascii=False)
            
            # 기간 변환: "20230605" → "2023-06-05"
            ps = data["period_start"]
            pe = data["period_end"]
            period_start = f"{ps[:4]}-{ps[4:6]}-{ps[6:8]}"
            period_end = f"{pe[:4]}-{pe[4:6]}-{pe[6:8]}"
            
            conn.execute(sql, {
                "category_name": category_name,
                "nice_codes": nice_codes_str,
                "summary_text": data["summary_text"],
                "keywords": keywords_json,
                "trademark_count": data.get("trademark_count", 0),
                "period_start": period_start,
                "period_end": period_end,
                "model_name": data.get("model_name", "EXAONE-3.5-2.4B-Instruct"),
                "generated_at": datetime.now()
            })
            
            print(f"  ✅ {category_name}")
    
    print(f"\n=== 완료 ===")


if __name__ == "__main__":
    main()
