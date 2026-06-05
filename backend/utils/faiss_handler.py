import os
import faiss
import numpy as np

# ==========================================
# 1. 절대 경로 자동 계산 시스템
# ==========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR) 

TEXT_INDEX_PATH = os.path.join(BACKEND_DIR, "index", "faiss_text.index")
IMAGE_INDEX_PATH = os.path.join(BACKEND_DIR, "index", "faiss_image.index")


# ==========================================
# 2. FAISS 검색 엔진 클래스 정의
# ==========================================
class FaissSearchEngine:
    def __init__(self, text_index_path: str, image_index_path: str):
        self.text_index_path = text_index_path
        self.image_index_path = image_index_path
        self.text_index = None
        self.image_index = None
        self._load_indices()

    def _load_indices(self):
        print("🚀 FAISS 검색 엔진 초기화 중...")

        if os.path.exists(self.text_index_path):
            self.text_index = faiss.read_index(self.text_index_path)
            print(f"✅ FAISS 텍스트 인덱스 로드 완료! (경로: {self.text_index_path})")
        else:
            raise FileNotFoundError(f"❌ 필수 에러: 텍스트 인덱스 파일을 찾을 수 없습니다: {self.text_index_path}")

        if os.path.exists(self.image_index_path):
            self.image_index = faiss.read_index(self.image_index_path)
            print(f"✅ FAISS 이미지 인덱스 로드 완료! (경로: {self.image_index_path})")
        else:
            print(f"⚠️ 안내: 이미지 인덱스 파일이 없습니다. 이미지 검색 기능은 비활성화 상태로 시작합니다. (경로: {self.image_index_path})")
            self.image_index = None

    # ------------------------------------------
    # 실제 검색 수행 메서드 (L2 거리 -> 유사도 변환 보정 장착)
    # ------------------------------------------
    def search_text(self, query_vector: np.ndarray, top_k: int = 5):
        """텍스트 벡터를 기반으로 유사 상표를 검색하고 유사도 점수를 반환합니다."""
        if self.text_index is None:
            raise ValueError("텍스트 인덱스가 로드되지 않아 검색할 수 없습니다.")
        
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
            
        query_vector = query_vector.astype('float32')
        
        # distances: 오리지널 L2 거리 값 반환 (똑같을수록 0에 수렴)
        distances, indices = self.text_index.search(query_vector, top_k)
        
        # 🔥 [핵심 수정] L2 거리를 0~1 사이의 유사도 점수로 변환
        # 거리가 0이면 점수는 1.0 / (1.0 + 0.0) = 1.0 (100%)이 됩니다.
        similarity_scores = 1.0 / (1.0 + distances)
        
        return similarity_scores, indices

    def search_image(self, query_vector: np.ndarray, top_k: int = 5):
        """이미지 벡터를 기반으로 유사 상표를 검색하고 유사도 점수를 반환합니다."""
        if self.image_index is None:
            raise ValueError("이미지 인덱스가 존재하지 않아 이미지 검색 기능을 사용할 수 없습니다.")
        
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
            
        query_vector = query_vector.astype('float32')
        
        distances, indices = self.image_index.search(query_vector, top_k)
        
        # 🔥 [핵심 수정] 이미지 인덱스도 L2 기반이므로 동일하게 유사도로 변환
        similarity_scores = 1.0 / (1.0 + distances)
        
        return similarity_scores, indices


# ==========================================
# 3. 전역(Singleton) 인스턴스 생성
# ==========================================
faiss_engine = FaissSearchEngine(
    text_index_path=TEXT_INDEX_PATH,
    image_index_path=IMAGE_INDEX_PATH
)