import { fetchWithAuthExpiry } from "./apiClient";

const BASE_URL = "http://localhost:5000";

export async function getSearchHistory({ token }) {
  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetchWithAuthExpiry(`${BASE_URL}/api/v1/detect/history`, {
    method: "GET",
    headers,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || `API 요청 실패: ${response.status}`);
  }

  return response.json();
}

export async function getMyPageActivities({ token }) {
  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetchWithAuthExpiry(`${BASE_URL}/api/v1/mypage/activities`, {
    method: "GET",
    headers,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || `API 요청 실패: ${response.status}`);
  }

  return response.json();
}
