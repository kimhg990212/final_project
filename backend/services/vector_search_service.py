import random
import numpy as np
from utils.faiss_handler import faiss_engine
from utils.database import SessionLocal
from sqlalchemy import text

def search_dissimilar_by_category(
    query_vector,
    nice_codes: list,
    style: str = "",
    top_k: int = 3
):
    try:
        nice_code_conditions = " OR ".join(
            [f"classification_code LIKE '%{code}%'" for code in nice_codes]
        )

        # 1단계: DB에서 업종 + 스타일 조건에 맞는 ID 전체 수집
        style_condition = ""
        if style == "이미지":
            style_condition = "AND (vienna_code IS NOT NULL AND vienna_code != '')"

        with SessionLocal() as db:
            id_rows = db.execute(
                text(f"""
                    SELECT id FROM trademark_trends
                    WHERE ({nice_code_conditions})
                    {style_condition}
                """)
            ).fetchall()

        candidate_ids = set(row[0] for row in id_rows)
        print(f"DB 필터 후 풀 크기: {len(candidate_ids)}건")

        # vienna_code 필터 결과가 너무 적으면 필터 해제
        if style == "이미지" and len(candidate_ids) < 10:
            with SessionLocal() as db:
                id_rows = db.execute(
                    text(f"SELECT id FROM trademark_trends WHERE ({nice_code_conditions})")
                ).fetchall()
            candidate_ids = set(row[0] for row in id_rows)
            print(f"vienna 필터 해제 후 풀 크기: {len(candidate_ids)}건")

        if not candidate_ids:
            return []

        # 2단계: FAISS 검색 — 풀 전체를 커버할 만큼 충분히 넓게 검색
        query = np.array(query_vector, dtype="float32").reshape(1, -1)
        search_k = min(len(candidate_ids) + 200, faiss_engine.text_index.ntotal)
        similarity_scores, indices = faiss_engine.search_text(query, top_k=search_k)
        print(f"FAISS 검색 범위: top {search_k}")

        # 3단계: 카테고리 풀과 교집합 → 유사도 순 정렬
        filtered = []
        for score, idx in zip(similarity_scores[0], indices[0]):
            if idx == -1:
                continue
            if int(idx) in candidate_ids:
                filtered.append({
                    "trademark_id": int(idx),
                    "similarity_score": float(score)
                })

        print(f"카테고리 내 유사도 후보: {len(filtered)}건")

        if not filtered:
            return []

        filtered.sort(key=lambda x: x["similarity_score"], reverse=True)
        top30 = filtered[:30]

        # 4단계: 상위 30개 메타데이터 DB에서 조회
        top_ids = tuple(f["trademark_id"] for f in top30)
        with SessionLocal() as db:
            rows = db.execute(
                text("""
                    SELECT id, title, applicant_name, application_date,
                           classification_code, image_url, big_image_url
                    FROM trademark_trends
                    WHERE id IN :ids
                """),
                {"ids": top_ids}
            ).mappings().all()

        db_map = {row["id"]: dict(row) for row in rows}

        results = []
        for f in top30:
            meta = db_map.get(f["trademark_id"])
            if not meta:
                continue
            results.append({
                "trademark_id": f["trademark_id"],
                "title": meta["title"],
                "applicant_name": meta["applicant_name"],
                "application_date": str(meta["application_date"]) if meta["application_date"] else None,
                "classification_code": meta["classification_code"],
                "image_url": meta["image_url"] or meta["big_image_url"],
                "similarity_score": round(f["similarity_score"], 4)
            })

        if not results:
            return []

        top1 = results[0]
        rest = results[1:]
        random_2 = random.sample(rest, min(2, len(rest)))
        return [top1] + random_2

    except Exception as e:
        print("에러 발생:", str(e))
        raise e