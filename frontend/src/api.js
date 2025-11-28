export async function apiGet(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getHealth() {
  return apiGet('/api/health');
}

export async function getProducts() {
  return apiGet('/api/products');
}

export async function getRates(base = 'EUR') {
  return apiGet(`/api/external/rates?base=${encodeURIComponent(base)}`);
}
