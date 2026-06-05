# backend/scripts/build_text_index.py
import os
import sys
import asyncio
import numpy as np
import faiss
from sqlalchemy import text

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
# Store FAISS indexes under backend/index for clearer separation
OUTPUT_DIR = os.path.join(BACKEND_DIR, "index")

sys.path.append(BACKEND_DIR)
from utils.ai_inference import embed_text
from utils.database import SessionLocal


def build_text_content(row) -> str:
    """
    [수정됨] 출원인(applicant_name), 캡션 등 다른 정보를 완전히 배제합니다.
    오직 상표명(title)만 추출하여 임베딩합니다.
    """
    title = row["title"] or ""
    title = title.strip()
    
    if title:
        return title
        
    # 상표명이 아예 비어있는 도형/로고 상표의 경우, 보조적으로 ocr_text만 사용
    ocr = row.get("ocr_text") or ""
    return ocr.strip()

async def build_faiss_text_index():
    print("🚀 DB 기반 텍스트 FAISS 인덱스 빌드 작업을 시작합니다...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with SessionLocal() as session:
        # Directly query the `trademark_trends` table (sync/ETL cached table)
        res = session.execute(text("SELECT id, application_number, title, applicant_name, caption, ocr_text FROM trademark_trends ORDER BY id"))
        metadata_records = res.mappings().all()

    total_count = len(metadata_records)
    print(f"📊 총 {total_count}건의 DB 메타데이터를 로드했습니다.")

    if total_count == 0:
        print("⚠️ DB에 적재된 상표 메타데이터가 없습니다. 먼저 데이터를 적재하세요.")
        return

    text_vectors = []
    text_ids = []

    for idx, metadata in enumerate(metadata_records, start=1):
        try:
            text_data = build_text_content(metadata)
            if not text_data:
                # 상표명도 없고 OCR 정보도 없으면 스킵 (출원인 이름은 절대 넣지 않음)
                print(f"⚠️ ID {metadata['id']}({metadata['application_number']})에 유효한 상표명(title)이 없어 건너뜁니다.")
                continue

            vector = await embed_text(text_data)
            text_vectors.append(vector)
            text_ids.append(metadata["id"])

            if idx % 100 == 0:
                print(f"⏳ {idx}/{total_count}건 텍스트 임베딩 완료...")

        except Exception as e:
            print(f"❌ ID {metadata['id']} 처리 중 오류: {e}")
            continue

    if not text_vectors:
        print("❌ 유효한 텍스트 벡터가 없어 인덱스를 생성하지 않습니다.")
        return

    text_np = np.array(text_vectors, dtype='float32')
    ids_np = np.array(text_ids, dtype='int64')
    
    # 모델 차원수에 맞게 인덱스 동적 생성
    text_index = faiss.IndexIDMap(faiss.IndexFlatL2(text_np.shape[1]))
    text_index.add_with_ids(text_np, ids_np)

    output_path = os.path.join(OUTPUT_DIR, "faiss_text.index")
    faiss.write_index(text_index, output_path)
    print(f"✅ DB 기반 텍스트 FAISS 인덱스 생성 완료! ({len(text_ids)}건) 경로: {output_path}")

if __name__ == "__main__":
    asyncio.run(build_faiss_text_index())