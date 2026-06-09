export function notifyAuthExpired() {
  window.dispatchEvent(new CustomEvent("auth:expired"));
}

export async function fetchWithAuthExpiry(input, init) {
  const response = await fetch(input, init);

  if (response.status === 401) {
    notifyAuthExpired();
  }

  return response;
}
