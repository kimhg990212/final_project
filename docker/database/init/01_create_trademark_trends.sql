-- ============================================================
-- 테이블: trademark_trends
-- 기능 : 업종별 트렌드 조회 (FR-10)
-- 설명 : KIPRIS 상표 출원 속보 API 데이터를 적재하는 캐시 테이블
-- ============================================================

CREATE TABLE IF NOT EXISTS trademark_trends (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    application_number  VARCHAR(30) NOT NULL UNIQUE,   -- 중복 방지 식별자
    title               VARCHAR(255),                  -- 상표명 (빌 수 있음)
    applicant_name      VARCHAR(255),                  -- 출원인
    application_date    VARCHAR(8),                    -- 출원일 "20260415"
    classification_code VARCHAR(255),                  -- 니스(업종) 필터
    vienna_code         VARCHAR(255),                  -- 도형코드 (여러 개 "|" 가능)
    application_status  VARCHAR(20),                   -- 출원/등록
    image_url           TEXT,                          -- drawing
    big_image_url       TEXT,                          -- bigDrawing
    ocr_text            TEXT,                          -- ★ OCR 추출 텍스트 (보조)
    caption             TEXT,                          -- ★ BLIP 캡션 (보조)
    synced_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_classification (classification_code),
    INDEX idx_application_date (application_date),
    INDEX idx_status (application_status)   -- 상표의 처리 상태(status)로 빠른 검색 위한 인덱스
);
