const BASE_URL = "http://localhost:5000";

export async function getSearchHistory() {
  const response = await fetch(`${BASE_URL}/api/v1/detect/history`, {
    method: "GET",
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || `API 요청 실패: ${response.status}`);
  }

  return response.json();
}
