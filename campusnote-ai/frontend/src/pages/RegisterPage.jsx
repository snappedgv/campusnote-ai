import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GraduationCap } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', semester: '', department: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form)
      navigate('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-navy-950 px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-500 to-blue-700 flex items-center justify-center text-white mb-3">
            <GraduationCap size={24} />
          </div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">Create your account</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Join CampusNote AI as a student</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white dark:bg-navy-900 border border-gray-200 dark:border-navy-800 rounded-2xl p-6 space-y-3 shadow-sm">
          {error && <div className="text-sm text-red-600 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-900 rounded-lg px-3 py-2">{error}</div>}

          <Field label="Full name" value={form.name} onChange={update('name')} placeholder="Jane Doe" required />
          <Field label="Email" type="email" value={form.email} onChange={update('email')} placeholder="you@college.edu" required />
          <Field label="Password" type="password" value={form.password} onChange={update('password')} placeholder="At least 6 characters" required />
          <div className="grid grid-cols-2 gap-3">
            <Field label="Semester" value={form.semester} onChange={update('semester')} placeholder="4" />
            <Field label="Department" value={form.department} onChange={update('department')} placeholder="AI & DS" />
          </div>

          <button
            type="submit" disabled={loading}
            className="w-full py-2.5 rounded-xl bg-accent-500 hover:bg-accent-600 disabled:opacity-60 text-white font-semibold text-sm transition-colors mt-2"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-5">
          Already have an account? <Link to="/login" className="text-accent-600 dark:text-accent-400 font-medium">Log in</Link>
        </p>
      </div>
    </div>
  )
}

function Field({ label, type = 'text', value, onChange, placeholder, required }) {
  return (
    <div>
      <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">{label}</label>
      <input
        type={type} required={required} value={value} onChange={onChange} placeholder={placeholder}
        className="w-full px-3 py-2.5 rounded-xl border border-gray-300 dark:border-navy-700 bg-white dark:bg-navy-800 text-sm focus:outline-none focus:ring-2 focus:ring-accent-500"
      />
    </div>
  )
}
