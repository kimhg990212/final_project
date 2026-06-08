const BASE_URL = "http://localhost:5000";

export async function generateTextLogo({ text, userId }) {
  const response = await fetch(`${BASE_URL}/text-logo/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
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
