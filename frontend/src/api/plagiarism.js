const BASE_URL = "http://localhost:5000";

export async function detectPlagiarism({ textQuery, imageFile }) {
  const formData = new FormData();

  if (textQuery) {
    formData.append("text_query", textQuery);
  }

  if (imageFile) {
    formData.append("image_file", imageFile);
  }

  const response = await fetch(`${BASE_URL}/api/v1/detect`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail || `API 요청 실패: ${response.status}`);
  }

  return response.json();
}
