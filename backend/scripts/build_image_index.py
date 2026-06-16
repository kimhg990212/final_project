import os
import sys
import asyncio
import tempfile
import requests
import numpy as np
import faiss
from urllib.parse import urlparse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
# Persist image FAISS index under backend/index
OUTPUT_INDEX_PATH = os.path.join(BACKEND_DIR, "index", "faiss_image.index")

sys.path.append(BACKEND_DIR)
from utils.ai_inference import embed_image
from utils.database import SessionLocal
from sqlalchemy import text


def is_remote_url(path: str) -> bool:
    if not path:
        return False
    parsed = urlparse(path)
    return parsed.scheme in {"http", "https"}


def download_remote_image(url: str) -> str:
    response = requests.get(url, stream=True, timeout=15)
    response.raise_for_status()
    suffix = os.path.splitext(urlparse(url).path)[1] or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                tmp.write(chunk)
        return tmp.name


def collect_image_sources(metadata) -> list[tuple[str, str]]:
    sources = []
    seen = set()

    for label, url in (
        ("image_url", metadata.get("image_url")),
        ("big_image_url", metadata.get("big_image_url")),
    ):
        if not url or url in seen:
            continue
        seen.add(url)
        sources.append((label, url))

    return sources


async def build_unified_image_index():
    print("🚀 DB 기반 이미지 FAISS 인덱스 빌드 작업을 시작합니다...")
    os.makedirs(os.path.dirname(OUTPUT_INDEX_PATH), exist_ok=True)

    with SessionLocal() as session:
        res = session.execute(text(
            "SELECT id, application_number, image_url, big_image_url "
            "FROM kipris_trademarks ORDER BY id"
        ))
        metadata_records = res.mappings().all()

    total_count = len(metadata_records)
    print(f"📊 총 {total_count}건의 DB 메타데이터를 로드했습니다.")

    if total_count == 0:
        print("⚠️ DB에 적재된 상표 메타데이터가 없습니다. 먼저 데이터를 적재하세요.")
        return

    results = []

    for idx, metadata in enumerate(metadata_records, start=1):
        image_sources = collect_image_sources(metadata)
        if not image_sources:
            print(f"⚠️ ID {metadata['id']}({metadata['application_number']})에 이미지 URL이 없습니다.")
            continue

        embedded_count = 0
        for source_label, image_url in image_sources:
            temp_path = None
            try:
                if is_remote_url(image_url):
                    temp_path = download_remote_image(image_url)
                    image_path = temp_path
                else:
                    image_path = image_url if os.path.exists(image_url) else None

                if not image_path or not os.path.exists(image_path):
                    print(f"⚠️ ID {metadata['id']} {source_label} 이미지 파일을 찾을 수 없습니다: {image_url}")
                    continue

                vector = await embed_image(image_path)
                results.append((vector, metadata["id"]))
                embedded_count += 1

            except Exception as e:
                print(f"❌ ID {metadata['id']} {source_label} 이미지 임베딩 실패: {e}")
                continue

            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

        if embedded_count == 0:
            print(f"⚠️ ID {metadata['id']}({metadata['application_number']})의 이미지 임베딩을 생성하지 못했습니다.")

        if idx % 100 == 0:
            print(f"⏳ {idx}/{total_count}건 처리 완료, 이미지 벡터 {len(results)}개 생성...")

    if not results:
        print("❌ 유효한 이미지 벡터가 없어 인덱스를 생성하지 않습니다.")
        return

    image_vectors, image_ids = zip(*results)
    image_np = np.array(image_vectors, dtype='float32')
    ids_np = np.array(image_ids, dtype='int64')

    index = faiss.IndexIDMap(faiss.IndexFlatL2(image_np.shape[1]))
    index.add_with_ids(image_np, ids_np)
    faiss.write_index(index, OUTPUT_INDEX_PATH)

    print(f"✅ DB 기반 이미지 FAISS 인덱스 생성 완료! ({len(image_ids)}건) 경로: {OUTPUT_INDEX_PATH}")


if __name__ == "__main__":
    asyncio.run(build_unified_image_index())
