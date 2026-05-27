from sqlalchemy import text

# get_trends_query → "페이지에 보여줄 N개의 행"을 가져옴 
# LIMIT :size OFFSET :offset        -- ★ 페이지 잘라내기
# 업종 코드 입력 없이 전체 조회할 수도 있으므로 classification or ""로 값을 설정
def get_trends_query(conn, classification, start_date, size, offset):
    """
    트렌드 목록 조회 — 업종·기간 필터 + 최신순 + 페이지네이션
    
    classification: 니스 분류 코드 (빈 문자열이면 전체)
    start_date:     기간 시작일 (YYYYMMDD 문자열, 예: "20250601")
    size:           한 페이지에 가져올 개수 (예: 20)
    offset:         건너뛸 개수 (예: 2페이지면 20)
    """
    return conn.execute(
        text("""
            SELECT id, application_number, title, applicant_name,
                   application_date, classification_code, vienna_code,
                   application_status, image_url, big_image_url, 
                   ocr_text, caption, synced_at
            FROM trademark_trends
            WHERE (:classification = '' OR classification_code LIKE CONCAT('%', :classification, '%'))
              AND application_date >= :start_date
            ORDER BY application_date DESC
            LIMIT :size OFFSET :offset
        """),
        {
            "classification": classification or "",
            "start_date":     start_date,
            "size":           size,
            "offset":         offset,
        },
    ).fetchall()

# count_trends_query → "조건에 맞는 전체 건수"만 셈
#  "위 조건의 결과 중 n번째부터 size개만 줘"
def count_trends_query(conn, classification, start_date):
    """
    같은 필터 조건으로 전체 건수만 세기 — 페이지네이션 총합 계산용
    """
    return conn.execute(
        text("""
            SELECT COUNT(*) AS cnt
            FROM trademark_trends
            WHERE (:classification = '' OR classification_code LIKE CONCAT('%', :classification, '%'))
              AND application_date >= :start_date
        """),
        {
            "classification": classification or "",
            "start_date":     start_date,
        },
    ).scalar()