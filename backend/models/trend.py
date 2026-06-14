from sqlalchemy import text

# 허용된 정렬 옵션 (화이트리스트)
SORT_CLAUSES = {
    "latest":    "application_date DESC", # 최신순  (출원일 내림차순)
    "oldest":    "application_date ASC", # 오래된순 (출원일 오름차순)
    "applicant": "REPLACE(REPLACE(applicant_name, '(주)', ''), ' ', '') ASC",   # 출원인순 (이름 가나다순) / "(주)" 제거 / 공백 제거
}

def get_trends_query(conn, classification, start_date, sort, size, offset):
    """
    트렌드 목록 조회 — 업종·기간 필터 + 최신순 + 페이지네이션
    
    classification: 니스 분류 코드 (빈 문자열이면 전체)
    start_date:     기간 시작일 (YYYYMMDD 문자열, 예: "20250601")
    size:           한 페이지에 가져올 개수 (예: 20)
    offset:         건너뛸 개수 (예: 2페이지면 20)
    """
    order_by = SORT_CLAUSES.get(sort, SORT_CLAUSES["latest"])   # 먼저 sort로 찾아보고, 못 찾으면 latest
    
    return conn.execute(
        text(f"""
            SELECT id, application_number, title, applicant_name,
                   application_date, classification_code, vienna_code,
                   application_status, image_url, big_image_url, 
                   synced_at
            FROM trademark_trends
            WHERE (:classification = '' OR classification_code LIKE CONCAT('%', :classification, '%'))
              AND application_date >= :start_date
            ORDER BY {order_by}
            LIMIT :size OFFSET :offset
        """),
        {
            "classification": classification or "",
            "start_date":     start_date,
            "size":           size,
            "offset":         offset,
        },
    ).fetchall()

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
                   
def get_summary_query(conn, classification):
    """
    트렌드 요약 조회 — 니스코드로 카테고리 매칭, 최신 1건
    
    classification: 니스 코드 (예: "25")
                   nice_codes "18,25,26,24,14" 에 포함되는지 검사
    """
    return conn.execute(
        text("""
            SELECT category_name, summary_text, keywords, 
                   period_start, period_end,
                   model_name, generated_at
            FROM trend_summaries
            WHERE FIND_IN_SET(:classification, nice_codes) > 0    
            ORDER BY generated_at DESC
            LIMIT 1
        """),
        {"classification": classification or ""},  
    ).fetchone()     

def get_classification_stats_query(conn, nice_codes):
    """카테고리 그룹 내 각 니스 코드별 출원 빈도"""
    results = []
    for code in nice_codes:
        count = conn.execute(
            text("""
                SELECT COUNT(*) AS cnt
                FROM trademark_trends
                WHERE classification_code LIKE :pattern
                  AND application_date >= '20230606'
                  AND application_date <= '20260606'
            """),
            {"pattern": f"%{code}%"},
        ).scalar()
        results.append({"code": code, "count": count or 0})
    return results