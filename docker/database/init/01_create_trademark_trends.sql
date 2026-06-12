-- ============================================================
-- 업종별 트렌드 조회 : 상표 트렌드 캐시 테이블
-- KIPRIS 상표 출원 속보 API 데이터를 적재(캐시)하며,
-- 이미지 분석으로 보강한 정보(ocr_text=OCR 추출 글자, caption=이미지 설명)도 함께 저장
-- ============================================================

CREATE TABLE IF NOT EXISTS trademark_trends (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    application_number  VARCHAR(30) NOT NULL UNIQUE,   
    title               VARCHAR(255),                  
    applicant_name      VARCHAR(255),                 
    application_date    VARCHAR(8),                    
    classification_code VARCHAR(255),                 
    vienna_code         VARCHAR(255),                  
    application_status  VARCHAR(20),                   
    image_url           TEXT,                          
    big_image_url       TEXT,                          
    ocr_text            TEXT,                         
    caption             TEXT,                          
    synced_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_classification (classification_code),
    INDEX idx_application_date (application_date),
    INDEX idx_status (application_status)   -- 상표의 처리 상태(status)로 빠른 검색 위한 인덱스
);