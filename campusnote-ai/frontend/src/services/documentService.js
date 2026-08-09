import api from './api'

export async function listDocuments() {
  const { data } = await api.get('/api/documents')
  return data
}

export async function uploadDocument(formData) {
  const { data } = await api.post('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function deleteDocument(id) {
  await api.delete(`/api/documents/${id}`)
}

export async function reindexDocument(id) {
  const { data } = await api.post(`/api/documents/${id}/reindex`)
  return data
}
