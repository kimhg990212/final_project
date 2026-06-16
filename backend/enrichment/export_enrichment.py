#kipris_trademarks 테이블에서 전체 컬럼 export하는 경우(팀 데이터 공유용)

import os
import sys
# 부모 폴더 (backend) 검색 경로에 추가(utils 임포트 위함)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
# load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))   # enrichment 폴더를 만들어 그 안에 다시 옮겼다 보니 아래 코드로 변경됨
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
#                                                    ^^
#                                                  상위 폴더
# __file__: C:\...\backend\enrichment\enrich_blip.py
# dirname: C:\...\backend\enrichment\
# .. (상위): C:\...\backend\
# .env: C:\...\backend\.env ✓

import json
from sqlalchemy import text
from utils.database import engine

print("전체 kipris_trademarks 데이터 내보내기...")

with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT application_number, title, applicant_name, application_date,
               classification_code, vienna_code, application_status,
               image_url, big_image_url, ocr_text, caption
        FROM kipris_trademarks
    """)).fetchall()

data = [
    {
        "application_number": row.application_number,
        "title": row.title or "",
        "applicant_name": row.applicant_name or "",
        "application_date": row.application_date or "",
        "classification_code": row.classification_code or "",
        "vienna_code": row.vienna_code or "",
        "application_status": row.application_status or "",
        "image_url": row.image_url or "",
        "big_image_url": row.big_image_url or "",
        "ocr_text": row.ocr_text or "",
        "caption": row.caption or ""
    }
    for row in rows
]

with open("kipris_trademarks_export.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 마지막에 통계 추가
ocr_count = sum(1 for d in data if d["ocr_text"])
caption_count = sum(1 for d in data if d["caption"])

print(f"\n{len(data)}개 행 → kipris_trademarks_export.json")
print(f"  OCR 채워진 행: {ocr_count}개")
print(f"  Caption 채워진 행: {caption_count}개")