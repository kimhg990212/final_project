# FR05 자연어 기반 로고 이미지 생성 기능

해당 기능의 관련된 모든 파일앞에 text_logo를 붙여놓았습니다.

## 1. 기능 개요

사용자가 입력한 자연어 설명을 기반으로 로고 이미지를 생성하는 기능입니다.

사용자는 원하는 브랜드명, 업종, 분위기, 색상, 스타일 등을 문장 형태로 입력할 수 있으며, 백엔드는 해당 자연어에서 핵심 키워드를 추출한 뒤 이미지 생성용 프롬프트로 변환합니다.

이후 AI 이미지 생성 모듈을 통해 로고 이미지를 생성하고, 생성된 이미지 경로와 프롬프트 정보를 반환합니다.

---

## 2. 담당 기능

- 자연어 기반 로고 생성 API 구현
- 사용자 입력 문장에서 핵심 키워드 추출
- 로고 생성용 프롬프트 생성
- AI 이미지 생성 로직 연동
- 생성된 이미지 파일 저장 및 경로 반환
- 생성 결과 데이터 구조 정의

---

```txt
backend/
 ├─ controllers/ API 요청을 처리하기 전후로 서비스 계층을 호출하고 응답 형태를 정리
 │   └─ download_controller.py        생성된 로고 사용자별 다운로드 기록을 관리
 │   └─ generate_controller.py        추천로고생성
 │   └─ google_auth_controller.py     구글로그인
 │   └─ plagiarism_controller.py      도용탐지
 │   └─ search_controller.py          추천로고를 위한 top3 조회
 │   └─ text_logo_controller.py       자연어->로고생성
 │   └─ trend.py                      트렌드 조회
 │   └─ upload_controllers.py         파일 업로드
 │
 ├─ enrichment/ 상표 데이터 보강, 키워드/캡션/추가 정보 생성 등 데이터 전처리 관련 기능 관리
 │   └─ enrich_blip.py
 │   └─ enrich_tesseract_ocr.py
 │   └─ export_enrichment.py
 │   └─ import_enrichment.py
 │   └─ import_trend_summaries.py
 │   └─ llm_input_data.json
 │   └─ llm_output_summaries_with_desc_140.json
 │   └─ prepare_llm_input.py
 │   └─ trademark_trends_export.json
 │
 ├─ index/ 검색 또는 벡터 인덱스 관련 파일 관리
 │   └─ faiss_image.index
 │   └─ faiss_text.index
 │
 ├─ middleware/ 전역 예외 처리, 요청/응답 처리 등 미들웨어 기능 관리
 │   └─ auth_middleware.py
 │   └─ error_middleware.py
 │
 ├─ models/     DB 테이블과 매핑되는 SQLAlchemy 모델 정의
 │   └─ domain.py
 │   └─ download_history.py
 │   └─ file_model.py
 │   └─ history_model.py
 │   └─ kipris_trademark.py
 │   └─ logo_model.py
 │   └─ result_model.py
 │   └─ schemas.py
 │   └─ text_logo_model.py
 │   └─ text_logo_image_result.py
 │   └─ trend.py
 │   └─ user.py
 │
 ├─ routes/     FastAPI API 엔드포인트 정의
 │   └─ admin_route.py
 │   └─ generate_route.py
 │   └─ google_auth.py
 │   └─ history_route.py
 │   └─ mypage_route.py
 │   └─ plagiarism_route.py
 │   └─ search_route.py
 │   └─ text_logo.py
 │   └─ trend.py
 │   └─ upload_route.py
 │   └─ user.py
 │
 ├─ schemas/    요청/응답 데이터 검증을 위한 Pydantic 스키마 정의
 │   └─ download_schema.py
 │   └─ google_auth.py
 │   └─ upload_schema.py
 │   └─ user.py
 │
 ├─ scripts/    데이터 적재, 초기 설정, 배치 실행 등 독립 실행 스크립트 관리
 │   └─ build_image_index.py
 │   └─ build_text_index.py
 │
 ├─ services/   주요 기능의 핵심 비즈니스 로직 처리
 │   └─ ai_service.py
 │   └─ download_service.py
 │   └─ embedding_service.py
 │   └─ file_service.py
 │   └─ history_service.py
 │   └─ image_generation_service.py
 │   └─ mypage_service.py
 │   └─ plagiarism_service.py
 │   └─ text_logo_service.py
 │   └─ trend.py
 │   └─ vector_search_service.py
 │
 ├─ static/generated/  추천로고 생성된 이미지 파일 저장 경로
 │
 ├─ uploads/images/  사용자가 업로드하거나 생성된 이미지 파일 저장 경로
 │
 ├─ utils/   공통 유틸 함수, 인증, DB 연결, 파일 처리 등 보조 기능 관리
 │   └─ ai_inference.py
 │   └─ auth.py
 │   └─ categories.py
 │   └─ database.py
 │   └─ faiss_handler.py
 │   └─ google_auth.py
 │   └─ llm_explanation.py
 │   └─ response_utils.py
 │   └─ text_logo_image_generator.py
 │   └─ text_logo_keyword_extractor.py
 │   └─ text_logo_prompt_builder.py
 │   └─ text_logo_text_composer.py
 │   └─ text_utils.py
 │
 ├─ vector_db/  FAISS 벡터 DB 및 벡터 검색 인덱스 관련 파일 관리
 │   └─ vector_loader.py
 │
 │
 │
 │
 │
 │
 ├─ .env                   실제 실행 환경변수 파일
 │
 ├─ .env.sample            팀원 공유용 환경변수 예시 파일
 │
 ├─ .gitignore             Git 추적 제외 파일 설정
 │
 ├─ config.py              프로젝트 설정값 관리
 │
 ├─ kipris_data_loader.py  KIPRIS 상표 데이터 적재 스크립트
 │
 ├─ main.py                FastAPI 서버 실행, 라우터 등록, CORS 및 정적 파일 설정
 │
 ├─ README.md              프로젝트 실행 및 기능 설명 문서
 │
 └─ requirement.txt        백엔드 실행에 필요한 Python 라이브러리 목록
```

## 3. 처리 흐름

```txt
사용자 자연어 입력
        ↓
키워드 추출
        ↓
로고 생성용 프롬프트 생성
        ↓
AI 이미지 생성
        ↓
이미지 파일 저장
        ↓
생성 결과 반환

backend/
 ├─ routes/
 │   └─ text_logo.py 자연어 기반 로고 생성 AIP 엔드포인트를 정의
 ├─ controllers/
 │   └─ text_logo_controller.py  클라이언트 요청을 받아 서비스 계층으로 전달하고, 처리 결과를 응답 형태로 반환
 ├─ services/
 │   └─ text_logo_service.py 자연어 기반 로고 생성 기능의 핵심 비즈니스 로직을 담당
 ├─ models/
 │   └─ text_logo_model.py 생성된 로고 이미지 정보를 저장하기 위한 데이터 모델을 정의
 └─ utils/
     ├─ text_logo_keyword_extractor.py 사용자 자연어 입력에서 로고 생서에 필요한 해교심 키워드 추출
     ├─ text_logo_prompt_builder.py 추출된 키워드를 기반으로 AI 이미지 생성에 적합한 프롬프트 생성
     └─ text_logo_file.py 생성된 이미지 파일을 저장하고, 클라이언트에 반환할 이미지 경로를 관리
```

```
#FR-08 흐름
사용자 스케치 이미지 업로드
+
사용자 자연어 입력
        ↓
이미지 벡터 추출 (CLIP)
        ↓
텍스트 벡터 추출 (CLIP)
        ↓
멀티모달 벡터 결합
        ↓
벡터 DB 내 비유사 로고 검색
        ↓
비유사 TOP5 로고 데이터 조회
        ↓
생성형 AI 프롬프트 구성
        ↓
Stable Diffusion 기반 로고 재생성
        ↓
생성 이미지 저장
        ↓
생성 결과 반환
        ↓
생성 이력 저장
```

#FR-08 백엔드 구조 및 파일 정의

```
backend/
 ├─ routes/
 │   ├─ generate_route.py
 │   │    사용자 스케치 이미지 및 자연어 입력을 받아
 │   │    이질적 로고 생성 기능 API 엔드포인트를 정의
 │   │
 │   └─ search_route.py
 │        사용자 입력 기반 비유사 로고 조회 API 엔드포인트를 정의
 │
 ├─ controllers/
 │   ├─ generate_controller.py
 │   │    멀티모달 벡터 생성, 비유사 로고 검색,
 │   │    AI 이미지 생성 기능을 순차적으로 호출하고
 │   │    생성 결과를 응답 형태로 반환
 │   │
 │   └─ search_controller.py
 │        멀티모달 벡터 생성 및 비유사 로고 검색을 수행하고
 │        조회 결과를 응답 데이터 형태로 반환
 │
 ├─ services/
 │   ├─ embedding_service.py
 │   │    사용자 스케치 이미지와 자연어 입력을
 │   │    CLIP 기반 임베딩 벡터로 변환하고,
 │   │    이미지 벡터와 텍스트 벡터를 결합
 │   │
 │   ├─ vector_search_service.py
 │   │    FAISS 기반 벡터 검색을 수행하며,
 │   │    공용 로고 데이터와 비교하여
 │   │    비유사 TOP5 로고 데이터를 반환
 │   │
 │   ├─ image_generation_service.py
 │   │    Stable Diffusion 기반 신규 로고 이미지를 생성
 │   │
 │   └─ history_service.py
 │        생성된 로고 이미지 및 사용자 입력 정보를 저장하고
 │        생성 이력 조회 기능을 관리
 │
 ├─ vector_db/
 │   └─ vector_loader.py
 │        공용 로고 벡터 데이터를
 │        FAISS 벡터 데이터베이스에 로딩하고
 │        벡터 검색 인덱스를 관리
 │
 ├─ models/
 │   ├─ history_model.py
 │   │    생성된 로고 이미지,
 │   │    사용자 프롬프트 및 생성 결과 정보를 저장하기 위한 데이터 모델 정의
 │   │
 │   └─ logo_model.py
 │        공용 로고 데이터셋의
 │        이미지 경로 및 벡터 정보를 저장하기 위한 데이터 모델 정의
 │
 ├─ utils/
 │   ├─ response_utils.py
 │   │    API 성공 및 실패 응답 형식을 표준화
 │   │
 │   ├─ similarity_utils.py
 │   │    벡터 간 거리 계산 및 유사도 산출 기능 처리
 │   │
 │   └─ image_utils.py
 │        이미지 전처리,
 │        포맷 변환 및 파일 저장 기능 처리
 │
 ├─ middleware/
 │   └─ error_middleware.py
 │        애플리케이션 전역 예외 처리를 수행하고
 │        오류 발생 시 일관된 JSON 응답 반환
 │
 ├─ static/
 │   └─ generated/
 │        생성된 로고 이미지 파일 저장 경로
 │
 ├─ requirements.txt
 │    AI 모델 및 FastAPI 실행에 필요한 라이브러리 관리
 │
 └─ main.py
      FastAPI 서버 실행 및
      전체 Route/Middleware 등록 관리
```
