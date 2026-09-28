const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

let apiKey = import.meta.env.VITE_API_KEY ?? '';

export function setApiKey(value: string) {
  apiKey = value.trim();
}

export async function apiFetch(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  if (apiKey) headers.set('X-API-Key', apiKey);
  return fetch(`${API_BASE_URL}${path}`, { ...init, headers });
}
