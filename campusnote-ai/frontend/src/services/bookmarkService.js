import api from './api'

export async function listBookmarks() {
  const { data } = await api.get('/api/bookmarks')
  return data
}

export async function createBookmark(payload) {
  const { data } = await api.post('/api/bookmarks', payload)
  return data
}

export async function deleteBookmark(id) {
  await api.delete(`/api/bookmarks/${id}`)
}
