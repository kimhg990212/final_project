// 백엔드 트렌드 API 주소
const BASE_URL = "http://localhost:5000";

/**
 * 트렌드 데이터 조회
 * @param {Object} params - 쿼리 파라미터
 * @param {string} params.classification - 업종 분류코드 (빈 문자열이면 전체)
 * @param {string} params.period - 기간 ("6m" | "1y" | "3y")
 * @param {number} params.page - 페이지 번호 (1부터)
 * @returns {Promise<Object>} - { data, total, page, size }
 */

export async function getTrends({
  classification = "",
  period = "1y",
  page = 1,
  sort = "latest",
}) {
  // URL 쿼리 문자열 만들기
  const queryString = new URLSearchParams({
    classification,
    period,
    page: String(page),
    sort,
  }).toString();

  const response = await fetch(`${BASE_URL}/trends?${queryString}`);

  // 에러 처리
  if (!response.ok) {
    throw new Error(`API 호출 실패: ${response.status}`);
  }

  // JSON 파싱해서 반환
  return await response.json();
}

/**
 * 트렌드 LLM 요약 조회
 * @param {Object} params - 쿼리 파라미터
 * @param {string} params.classification - 업종 분류코드 (빈 값이면 null 반환)
 * @returns {Promise<Object|null>} - { category_name, summary_text, keywords, ... } 또는 null
 */
export async function getTrendSummary({ classification = "" }) {
  if (!classification) return null;

  const queryString = new URLSearchParams({ classification }).toString();
  const response = await fetch(`${BASE_URL}/trends/summary?${queryString}`);

  if (!response.ok) {
    throw new Error(`요약 API 호출 실패: ${response.status}`);
  }

  return await response.json();
}

/**
 * 트렌드 색상 분석 조회
 */
export async function getTrendColors({ classification = "" }) {
  if (!classification) {
    return null;
  }

  const queryString = new URLSearchParams({ classification }).toString();
  const response = await fetch(`${BASE_URL}/trends/colors?${queryString}`);

  if (!response.ok) {
    throw new Error(`색상 API 호출 실패: ${response.status}`);
  }

  return await response.json();
}

/**
 * 분류 코드별 출원 빈도 시각화용 데이터 조회
 * - 카테고리(니스 그룹) 내 각 니스 코드별 출원 수 집계
 * - 응답: [{code: "05", count: 1234}, ...]
 */

export async function getTrendClassificationStats({ classification = "" }) {
  if (!classification) return null;
  const queryString = new URLSearchParams({ classification }).toString();
  const response = await fetch(
    `${BASE_URL}/trends/classification-stats?${queryString}`,
  );
  if (!response.ok) throw new Error(`분류 빈도 API 실패: ${response.status}`);
  return await response.json();
}
