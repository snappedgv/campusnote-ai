import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { login as loginApi, register as registerApi, fetchMe } from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const bootstrap = useCallback(async () => {
    const token = localStorage.getItem('campusnote_token')
    if (!token) {
      setLoading(false)
      return
    }
    try {
      const me = await fetchMe()
      setUser(me)
    } catch {
      localStorage.removeItem('campusnote_token')
      localStorage.removeItem('campusnote_user')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    bootstrap()
  }, [bootstrap])

  const login = async (email, password) => {
    const data = await loginApi(email, password)
    localStorage.setItem('campusnote_token', data.access_token)
    const me = await fetchMe()
    setUser(me)
    return me
  }

  const register = async (payload) => {
    const data = await registerApi(payload)
    localStorage.setItem('campusnote_token', data.access_token)
    const me = await fetchMe()
    setUser(me)
    return me
  }

  const logout = () => {
    localStorage.removeItem('campusnote_token')
    localStorage.removeItem('campusnote_user')
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAdmin: user?.role === 'admin' }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
