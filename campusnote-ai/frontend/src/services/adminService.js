import api from './api'

export async function semanticSearch(q, filters = {}) {
  const { data } = await api.get('/api/search', { params: { q, ...filters } })
  return data
}

export async function getAdminStats() {
  const { data } = await api.get('/api/admin/stats')
  return data
}
