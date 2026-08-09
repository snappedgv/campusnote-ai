import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GraduationCap } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const me = await login(email, password)
      navigate(me.role === 'admin' ? '/admin' : '/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-navy-950 px-4">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-500 to-blue-700 flex items-center justify-center text-white mb-3">
            <GraduationCap size={24} />
          </div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">Welcome back</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Log in to CampusNote AI</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white dark:bg-navy-900 border border-gray-200 dark:border-navy-800 rounded-2xl p-6 space-y-4 shadow-sm">
          {error && <div className="text-sm text-red-600 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-900 rounded-lg px-3 py-2">{error}</div>}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">Email</label>
            <input
              type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-gray-300 dark:border-navy-700 bg-white dark:bg-navy-800 text-sm focus:outline-none focus:ring-2 focus:ring-accent-500"
              placeholder="you@college.edu"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">Password</label>
            <input
              type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl border border-gray-300 dark:border-navy-700 bg-white dark:bg-navy-800 text-sm focus:outline-none focus:ring-2 focus:ring-accent-500"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit" disabled={loading}
            className="w-full py-2.5 rounded-xl bg-accent-500 hover:bg-accent-600 disabled:opacity-60 text-white font-semibold text-sm transition-colors"
          >
            {loading ? 'Logging in...' : 'Log In'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-5">
          Don't have an account? <Link to="/register" className="text-accent-600 dark:text-accent-400 font-medium">Sign up</Link>
        </p>
        <p className="text-center text-xs text-gray-400 dark:text-gray-500 mt-2">
          Admin accounts are created via the seed script, not public registration.
        </p>
      </div>
    </div>
  )
}
