export type OfferQuery = {
  query?: string;
  market?: string;
  max_price?: string;
  region?: string;
};

export type AlertInput = {
  product_id: number;
  threshold: number;
  channel: "email" | "push" | "webhook";
};

const API_BASE = "http://localhost:8000";

async function fetchJson(path: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  if (response.status === 204) return null;
  return response.json();
}

export async function getOffers(query: OfferQuery) {
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  return fetchJson(`/offers?${params.toString()}`);
}

export async function getProductHistory(productId: number) {
  return fetchJson(`/products/${productId}/history`);
}

export async function createAlert(payload: AlertInput) {
  return fetchJson("/alerts", { method: "POST", body: JSON.stringify(payload) });
}
