# 변경사항 기록

## 2026-06-16

### 1. Google 로그인 설정 (환경변수)

**`frontend/.env`** — 신규 생성
- `VITE_GOOGLE_CLIENT_ID` 추가
- Google Cloud Console의 OAuth 2.0 클라이언트 ID 설정
- 이 파일이 없으면 헤더에 "Google 로그인 불가" 비활성 버튼이 표시됨

**`backend/.env`**
- `GOOGLE_CLIENT_ID` 추가 (백엔드 토큰 검증용)
- 기존에 `VITE_GOOGLE_CLIENT_ID`로 잘못 입력되어 있던 키 이름을 수정
- `backend/utils/google_auth.py`의 `os.getenv("GOOGLE_CLIENT_ID")`와 일치하도록 변경

---

### 2. 로고 추천 검색 로직 수정

**`backend/services/vector_search_service.py`**

| | 변경 전 | 변경 후 |
|---|---|---|
| 추출 방식 | top30에서 완전 랜덤 3개 | **유사도 1등 1개 + 나머지 중 랜덤 2개** |
| DB 테이블 | `kipris_trademarks` | `trademark_trends` (FAISS 인덱스와 동일 테이블로 통일) |

---

### 3. 로고 생성 이미지 고도화

#### 3-1. `backend/services/image_generation_service.py` — 전면 재작성

| 문제 | 변경 전 | 변경 후 |
|---|---|---|
| 블렌딩 방식 | 픽셀 평균 블렌딩 (ghosting 발생) | **1등 이미지만 init_image 전달** |
| 2·3등 이미지 활용 | 미사용 | **주요 색상 추출 → 프롬프트에 반영** |
| 브랜드 설명 언어 | 한국어 그대로 영어 프롬프트에 삽입 | **OpenAI API로 영어 번역 후 삽입** (실패 시 원문 fallback) |
| 생성 이미지 수 | 1개 | **3개** |
| 이미지 전달 크기 | 1024×1024 | **768×768** (OOM 방지) |

추가된 함수:
- `translate_to_english()` — OpenAI gpt-3.5-turbo로 번역
- `get_color_hint()` — PIL quantize로 배경 제외 주요 색상 hex 추출
- `get_init_image_b64()` — 1등 이미지 다운로드 후 768×768 base64 변환

#### 3-2. `backend/controllers/generate_controller.py`

| | 변경 전 | 변경 후 |
|---|---|---|
| DB 테이블 | `kipris_trademarks` | `trademark_trends` |
| 이미지 URL 순서 | DB 반환 순서 (랜덤) | **trademark_ids 입력 순서 유지 (1등 먼저)** |

#### 3-3. `colab_server.ipynb` (셀 2)

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| 이미지 크기 | 1024×1024 | **768×768** (VRAM 절약, OOM 방지) |
| strength | 0.75 | **0.55** (init_image 스타일 더 많이 반영) |
| guidance_scale | 10.0 | **8.0** |
| num_inference_steps | 50 | **30** (속도 개선 + 메모리 절약) |
| num_images 기본값 | 2 | **3** |
| `enable_vae_tiling()` | deprecated 방식 | `pipe.vae.enable_tiling()` 로 수정 |
| `torch.cuda.empty_cache()` | 루프 내부에만 | **루프 진입 전 + 루프 내부** 모두 호출 |

#### 3-4. `frontend/src/pages/RecommendPage.jsx`

- `"비유사 TOP3 상표"` → `"참고 TOP3 상표"` (실제 로직은 유사도 기반이므로 라벨 수정)

---

### 전체 로고 추천 흐름 (최종)

```
업종 선택 + 브랜드 설명 입력
        ↓
업종코드(NICE 분류) 필터링
        ↓
브랜드 설명 텍스트 임베딩 → FAISS 검색 → 상위 100개
        ↓
trademark_trends 테이블 업종코드 필터 → top30 추출
        ↓
유사도 1등(고정) + 나머지 29개 중 랜덤 2개 = 최종 3개
        ↓
브랜드 설명 한→영 번역 (OpenAI API)
2·3등 이미지에서 주요 색상 추출 → 프롬프트에 반영
1등 이미지 768×768 다운로드 → base64 변환 (init_image)
        ↓
[프롬프트 + init_image] → Colab SDXL img2img (strength=0.55, steps=30)
        ↓
로고 이미지 3개 생성 및 저장 → 사용자 선택
```

---

### 관련 파일 목록

| 파일 | 역할 |
|---|---|
| `frontend/src/pages/RecommendPage.jsx` | 추천 페이지 UI |
| `frontend/src/api/recommend.js` | API 호출 |
| `backend/routes/search_route.py` | `/search/logo`, `/search/categories` 라우트 |
| `backend/controllers/search_controller.py` | 검색 로직 진입점 |
| `backend/services/vector_search_service.py` | top30 추출, 1등+랜덤2개 선별 |
| `backend/services/embedding_service.py` | 브랜드 설명 텍스트 임베딩 |
| `backend/utils/faiss_handler.py` | FAISS 검색 실행 |
| `backend/utils/categories.py` | 업종명 → NICE 코드 변환 |
| `backend/routes/generate_route.py` | `/generate/logo` 라우트 |
| `backend/controllers/generate_controller.py` | DB에서 상표 이미지 조회 |
| `backend/services/image_generation_service.py` | 번역, 색상 추출, Colab 호출 |
| `colab_server.ipynb` | SDXL img2img 생성 서버 |
