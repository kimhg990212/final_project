import faiss
import numpy as np

# CLIP 벡터 차원
dimension = 512

# FAISS 인덱스 생성
index = faiss.IndexFlatL2(
    dimension
)

# 벡터 로드
vectors = np.load(
    "app/vector_db/logo_vectors.npy"
).astype("float32")

# FAISS에 추가
index.add(vectors)

print("벡터 로딩 완료")
print("총 벡터 수:", index.ntotal)