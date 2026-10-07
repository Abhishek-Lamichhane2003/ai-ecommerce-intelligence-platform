const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail || `Request failed: ${response.status}`)
  }
  return payload
}

export const api = {
  status: () => request('/api/status'),
  overview: () => request('/api/overview'),
  sales: () => request('/api/sales'),
  customers: () => request('/api/customers'),
  segmentation: () => request('/api/segmentation'),
  preview: () => request('/api/data-preview?limit=50'),
  aiQuery: (question) => request('/api/ai/query', {
    method: 'POST',
    body: JSON.stringify({ question }),
  }),
  aiHistory: () => request('/api/ai/history'),
}
