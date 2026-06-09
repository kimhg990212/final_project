import { fetchWithAuthExpiry } from "./apiClient";

const BASE_URL = "http://localhost:5000";

export async function detectPlagiarism({
  trademarkName,
  textQuery,
  imageFile,
  token,
}) {
  const formData = new FormData();

  if (trademarkName) {
    formData.append("trademark_name", trademarkName);
  }

  if (textQuery) {
    formData.append("text_query", textQuery);
  }

  if (imageFile) {
    formData.append("image_file", imageFile);
  }

  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetchWithAuthExpiry(`${BASE_URL}/api/v1/detect`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || `API 요청 실패: ${response.status}`);
  }

  return response.json();
}
