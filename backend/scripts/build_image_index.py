# backend/scripts/build_image_index.py
import os
import sys
import json
import asyncio
import numpy as np
import faiss
from pathlib import Path

# 경로 설정
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)

LABEL_ROOT = os.path.join(BACKEND_DIR, "data", "상표이미지_라벨")
SOURCE_ROOT = os.path.join(BACKEND_DIR, "data", "상표이미지_원천")
OUTPUT_INDEX_PATH = os.path.join(BACKEND_DIR, "data", "faiss_image.index")

# 모듈 로드
sys.path.append(BACKEND_DIR)
from backend.utils.ai_inference import embed_image

async def build_unified_image_index():
    print("🚀 데이터셋 통합 인덱싱을 시작합니다...")
    
    # 1. 원천 폴더의 모든 이미지 경로 매핑 (재귀 탐색)
    print("🔍 원천 이미지 파일 탐색 중 (시간이 소요될 수 있습니다)...")
    img_map = {p.name: p for p in Path(SOURCE_ROOT).rglob("*.*") if p.suffix.lower() in ['.jpg', '.png', '.jpeg']}
    print(f"✅ 총 {len(img_map)}개의 이미지 파일을 매핑했습니다.")
    
    results = [] # (vector, id) 튜플 저장용
    
    # 2. 라벨 폴더 JSON 탐색
    json_files = list(Path(LABEL_ROOT).rglob("*.json"))
    print(f"📂 총 {len(json_files)}개의 라벨 묶음을 발견했습니다.")

    for idx, json_path in enumerate(json_files):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for img_info in data.get('images', []):
            file_name = img_info.get('fileName')
            img_id = img_info.get('id')
            
            # 매핑된 경로에서 이미지 확인
            img_path = img_map.get(file_name)
            
            if img_path and img_path.exists():
                try:
                    # 이미지 임베딩 실행
                    i_vec = await embed_image(str(img_path))
                    results.append((i_vec, int(img_id)))
                except Exception as e:
                    print(f"❌ 임베딩 오류 스킵 ({file_name}): {str(e)[:30]}...")
                    continue
        
        if (idx + 1) % 10 == 0:
            print(f"⏳ 진행 중... ({idx + 1}/{len(json_files)} 폴더 처리)")

    # 3. 데이터 동기화 및 FAISS 저장
    if results:
        image_vectors, valid_image_ids = zip(*results)
        image_np = np.array(image_vectors).astype('float32')
        image_ids_np = np.array(valid_image_ids).astype('int64')
        
        print(f"💾 {len(image_np)}개의 이미지 데이터 인덱싱 시작...")
        
        # FAISS 인덱스 생성 (512차원)
        index = faiss.IndexIDMap(faiss.IndexFlatL2(512))
        index.add_with_ids(image_np, image_ids_np)
        
        # 결과 저장
        faiss.write_index(index, OUTPUT_INDEX_PATH)
        print(f"✨ 완료! 인덱스 파일 생성 성공: {OUTPUT_INDEX_PATH}")
    else:
        print("⚠️ 유효한 이미지 데이터가 없습니다. 경로를 다시 확인해주세요.")

if __name__ == "__main__":
    asyncio.run(build_unified_image_index())