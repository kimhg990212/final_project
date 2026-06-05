const BASE_URL = "http://localhost:5000";

export async function googleLogin({ token }) {
  const response = await fetch(`${BASE_URL}/users/google/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ token }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || "API 요청에 실패하였습니다. 잠시후 시도해주세요.");
  }

  return response.json();
}

export async function getGoogleMe({ token }) {
  const response = await fetch(`${BASE_URL}/users/google/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || "API 요청에 실패하였습니다. 잠시후 시도해주세요.");
  }

  return response.json();
}
