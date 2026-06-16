const BASE_URL = "http://localhost:5000";

export async function getCategories() {
  const res = await fetch(`${BASE_URL}/search/categories`);
  const data = await res.json();
  if (!data.success) throw new Error(data.message);
  return data.data.categories;
}

export async function searchLogo({ categoryName, brandDescription, style }) {
  const form = new FormData();
  form.append("category_name", categoryName);
  form.append("brand_description", brandDescription);
  if (style) form.append("style", style);

  const res = await fetch(`${BASE_URL}/search/logo`, {
    method: "POST",
    body: form,
  });
  const data = await res.json();
  if (!data.success) throw new Error(data.message);
  return data.data.results;
}

export async function generateLogo({
  trademarkIds,
  brandDescription,
  style,
}) {
  const form = new FormData();
  form.append("trademark_ids", trademarkIds.join(","));
  form.append("brand_description", brandDescription);
  if (style) form.append("style", style);

  const res = await fetch(`${BASE_URL}/generate/logo`, {
    method: "POST",
    body: form,
  });
  const data = await res.json();
  if (!data.success) throw new Error(data.message);
  return data.data.generated_images;
}
