import { fetchWithAuthExpiry } from "./apiClient";

const BASE_URL = "http://localhost:5000";

export async function generateTextLogo({ logoName, text, userId }) {
  const response = await fetch(`${BASE_URL}/text-logo/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      logo_name: logoName,
      text,
      user_id: userId,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || "로고 생성에 실패했습니다.");
  }

  return response.json();
}

export async function saveDownloadHistory({
  token,
  userId,
  resultId,
  prompt,
  imagePath,
}) {
  const response = await fetchWithAuthExpiry(`${BASE_URL}/generate/download`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      user_id: userId,
      result_id: resultId,
      prompt,
      image_path: imagePath,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || "다운로드 기록 저장에 실패했습니다.");
  }

  return response.json();
}
