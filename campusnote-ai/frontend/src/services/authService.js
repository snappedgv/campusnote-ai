import api from './api'

export async function login(email, password) {
  const { data } = await api.post('/api/auth/login', { email, password })
  return data
}

export async function register({ name, email, password, semester, department }) {
  const { data } = await api.post('/api/auth/register', { name, email, password, semester, department })
  return data
}

export async function fetchMe() {
  const { data } = await api.get('/api/auth/me')
  return data
}
