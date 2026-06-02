# backend/scripts/build_text_index.py
import os
import sys
import asyncio
import pandas as pd
import numpy as np
import faiss

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)

CSV_FILE_PATH = os.path.join(BACKEND_DIR, "data", "Label_1_Validation_Labeling.csv")
OUTPUT_DIR = os.path.join(BACKEND_DIR, "data")

sys.path.append(BACKEND_DIR)
# 이미지 임베딩 제외, 텍스트 임베딩 함수만 임포트
from backend.utils.ai_inference import embed_text

async def build_faiss_text_index():
    print("🚀 텍스트 전용 FAISS 인덱스 빌드 작업을 시작합니다...")
    
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ 에러: CSV 파일이 없습니다: {CSV_FILE_PATH}")
        return
        
    df = pd.read_csv(CSV_FILE_PATH, encoding='cp949')
    print(f"📊 총 {len(df)}건의 상표 행 데이터를 로드했습니다.")

    # 텍스트 저장소만 단독 운영
    text_vectors, valid_text_ids = [], []

    for idx, row in df.iterrows():
        try:
            if pd.isna(row['patent_id']):
                continue
            record_id = int(float(row['patent_id'])) 

            # 1. 텍스트 정제 및 임베딩
            korean_text = str(row['korean']).strip() if pd.notna(row['korean']) else ""
            english_text = str(row['english']).strip() if pd.notna(row['english']) else ""
            text_data = f"{korean_text} {english_text}".replace("-", "").strip()
            
            if not text_data:
                if pd.notna(row.get('rejectionContentDetail')):
                    text_data = str(row['rejectionContentDetail'])[:50]
                else:
                    print(f"⚠️ 경고: {record_id}번 데이터는 텍스트가 없어 인덱스에서 제외합니다.")
                    continue # 데이터가 없으면 인덱스에 넣지 않음

            t_vec = await embed_text(text_data)
            text_vectors.append(t_vec)
            valid_text_ids.append(record_id)
            
            # 진행 상황 (100건 단위)
            if (idx + 1) % 100 == 0:
                print(f"⏳ 현재 {idx + 1}번째 텍스트 데이터 처리 중...")

        except Exception as e:
            print(f"❌ 라인 {idx}번 데이터 처리 중 에러 발생: {e}")
            continue

    # 2. FAISS 텍스트 인덱스 빌드 및 저장
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    text_vector_dim = 768 # ko-sroberta-multitask의 차원
    
    if text_vectors:
        text_np = np.array(text_vectors).astype('float32')
        text_ids_np = np.array(valid_text_ids).astype('int64')
        text_index = faiss.IndexIDMap(faiss.IndexFlatL2(text_vector_dim))
        text_index.add_with_ids(text_np, text_ids_np)
        
        output_path = os.path.join(OUTPUT_DIR, "faiss_text.index")
        faiss.write_index(text_index, output_path)
        print(f"✅ 텍스트 전용 인덱스 빌드 완료! ({len(valid_text_ids)}건 저장됨)")
    else:
        print("💡 생성된 텍스트 벡터가 없어 인덱스를 저장하지 않았습니다.")

    print("✨ FAISS 텍스트 스크립트 실행이 종료되었습니다.")

if __name__ == "__main__":
    asyncio.run(build_faiss_text_index())