-- ===================================================
-- 카테고리별 트렌드 분석 : LLM(EXAONE) 분석 내용 저장
-- ===================================================
CREATE TABLE IF NOT EXISTS trend_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,         -- 카테고리 이름 예) "패션·잡화"
    nice_codes VARCHAR(100),                    -- 니스 코드 "18,25,26,24,14" 콤마 구분
    summary_text TEXT NOT NULL,                 -- LLM 생성 요약
    keywords JSON,                              -- 키워드 JSON ["친환경", "K-스트리트", ...]
    trademark_count INT,                        -- 분석에 쓰인 상표 수
    period_start DATE,                          -- 분석 기간 시작
    period_end DATE,                            -- 분석 기간 끝
    model_name VARCHAR(50),                     -- "EXAONE-3.5-2.4B-Instruct"
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_category_period (category_name, period_start, period_end),  -- 제약조건: 같은 (카테고리명, 기간 시작, 기간 끝) 조합은 딱 1개 행만 허용
    INDEX idx_category (category_name),  -- category_name 단독 검색 빠르게 하는 인덱스 추가
    INDEX idx_period (period_start, period_end)  -- 기간(start+end) 검색 빠르게 하는 인덱스 추가
);