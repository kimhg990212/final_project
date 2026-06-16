# kipris_trademarks 테이블에서 전체 컬럼 import 하는 경우(전체 데이터 공유 버전)

import os
import sys
# 부모 폴더 (backend) 검색 경로에 추가(utils 임포트 위함)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
#load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))   # enrichment 폴더를 만들었다 보니
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

print("kipris_trademarks_export.json 불러오기...")

with open("kipris_trademarks_export.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"{len(data)}개 행 처리 중...")

with engine.begin() as conn:
    for i, item in enumerate(data, 1):
        conn.execute(text("""
            INSERT INTO kipris_trademarks (
                application_number, title, applicant_name, application_date,
                classification_code, vienna_code, application_status,
                image_url, big_image_url, ocr_text, caption
            )
            VALUES (
                :app_num, :title, :applicant_name, :application_date,
                :classification_code, :vienna_code, :application_status,
                :image_url, :big_image_url, :ocr_text, :caption
            )
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                applicant_name = VALUES(applicant_name),
                application_date = VALUES(application_date),
                classification_code = VALUES(classification_code),
                vienna_code = VALUES(vienna_code),
                application_status = VALUES(application_status),
                image_url = VALUES(image_url),
                big_image_url = VALUES(big_image_url),
                ocr_text = VALUES(ocr_text),
                caption = VALUES(caption)
        """), {
            "app_num": item["application_number"],
            "title": item["title"],
            "applicant_name": item["applicant_name"],
            "application_date": item["application_date"],
            "classification_code": item["classification_code"],
            "vienna_code": item["vienna_code"],
            "application_status": item["application_status"],
            "image_url": item["image_url"],
            "big_image_url": item["big_image_url"],
            "ocr_text": item["ocr_text"],
            "caption": item["caption"]
        })
        
        if i % 50 == 0:
            print(f"  {i}/{len(data)}개 처리됨...")

print(f"\n완료! 총 {len(data)}개 행 import")