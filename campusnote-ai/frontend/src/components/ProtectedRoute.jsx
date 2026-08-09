import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <FullScreenLoader />
  if (!user) return <Navigate to="/login" replace />
  return children
}

export function AdminRoute({ children }) {
  const { user, loading, isAdmin } = useAuth()
  if (loading) return <FullScreenLoader />
  if (!user) return <Navigate to="/login" replace />
  if (!isAdmin) return <Navigate to="/dashboard" replace />
  return children
}

export function FullScreenLoader() {
  return (
    <div className="h-screen w-screen flex items-center justify-center bg-white dark:bg-navy-950">
      <div className="flex gap-1.5">
        <span className="w-2.5 h-2.5 rounded-full bg-accent-500 typing-dot" />
        <span className="w-2.5 h-2.5 rounded-full bg-accent-500 typing-dot" />
        <span className="w-2.5 h-2.5 rounded-full bg-accent-500 typing-dot" />
      </div>
    </div>
  )
}
