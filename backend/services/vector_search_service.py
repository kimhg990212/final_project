import random
import numpy as np
from utils.faiss_handler import faiss_engine
from utils.database import SessionLocal
from sqlalchemy import text

def search_dissimilar_by_category(
    query_vector,
    nice_codes: list,
    top_k: int = 3
):
    try:
        query = np.array(query_vector, dtype="float32").reshape(1, -1)

        similarity_scores, indices = faiss_engine.search_text(query, top_k=100)
        print("FAISS 검색 완료:", len(indices[0]))

        candidates = []
        for score, idx in zip(similarity_scores[0], indices[0]):
            if idx == -1:
                continue
            candidates.append({
                "trademark_id": int(idx),
                "similarity_score": float(score)
            })
        print("후보 수:", len(candidates))

        if not candidates:
            return []

        trademark_ids = [c["trademark_id"] for c in candidates]
        nice_code_conditions = " OR ".join(
            [f"classification_code LIKE '%{code}%'" for code in nice_codes]
        )
        print("니스 코드 조건:", nice_code_conditions)

        with SessionLocal() as db:
            result = db.execute(
                text(f"""
                    SELECT id, title, applicant_name, application_date,
                           classification_code, image_url, big_image_url
                    FROM kipris_trademarks
                    WHERE id IN :ids
                    AND ({nice_code_conditions})
                """),
                {"ids": tuple(trademark_ids)}
            )
            rows = result.mappings().all()
        print("DB 결과 수:", len(rows))

        db_map = {row["id"]: dict(row) for row in rows}

        filtered = []
        for c in candidates:
            if c["trademark_id"] in db_map:
                meta = db_map[c["trademark_id"]]
                filtered.append({
                    "trademark_id": c["trademark_id"],
                    "title": meta["title"],
                    "applicant_name": meta["applicant_name"],
                    "application_date": str(meta["application_date"]) if meta["application_date"] else None,
                    "classification_code": meta["classification_code"],
                    "image_url": meta["image_url"] or meta["big_image_url"],
                    "similarity_score": round(c["similarity_score"], 4)
                })

        # 상위 30개에서 랜덤 3개 추출
        filtered.sort(key=lambda x: x["similarity_score"], reverse=True)
        top30 = filtered[:30]
        random_3 = random.sample(top30, min(3, len(top30)))
        return random_3

    except Exception as e:
        print("에러 발생:", str(e))
        raise e