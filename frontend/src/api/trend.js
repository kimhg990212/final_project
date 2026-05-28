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
}) {
  // URL 쿼리 문자열 만들기
  const queryString = new URLSearchParams({
    classification,
    period,
    page: String(page),
  }).toString();

  // 백엔드 호출
  const response = await fetch(`${BASE_URL}/trends?${queryString}`);

  // 에러 처리
  if (!response.ok) {
    throw new Error(`API 호출 실패: ${response.status}`);
  }

  // JSON 파싱해서 반환
  return await response.json();
}
