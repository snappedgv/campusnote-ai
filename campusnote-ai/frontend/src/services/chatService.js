import api from './api'

export async function sendChatMessage(payload) {
  const { data } = await api.post('/api/chat', payload)
  return data
}

export async function listChats() {
  const { data } = await api.get('/api/chats')
  return data
}

export async function getChat(chatId) {
  const { data } = await api.get(`/api/chats/${chatId}`)
  return data
}

export async function deleteChat(chatId) {
  await api.delete(`/api/chats/${chatId}`)
}

export async function renameChat(chatId, title) {
  const { data } = await api.put(`/api/chats/${chatId}/rename`, null, { params: { title } })
  return data
}
