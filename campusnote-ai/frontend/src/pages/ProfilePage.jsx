import React from 'react'
import { User, Mail, GraduationCap, Building2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'

export default function ProfilePage() {
  const { user } = useAuth()

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-lg mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-6">Profile</h1>
        <div className="rounded-2xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 p-6 space-y-4">
          <Row icon={User} label="Name" value={user?.name} />
          <Row icon={Mail} label="Email" value={user?.email} />
          <Row icon={GraduationCap} label="Semester" value={user?.semester || '—'} />
          <Row icon={Building2} label="Department" value={user?.department || '—'} />
          <Row icon={User} label="Role" value={user?.role} />
        </div>
      </div>
    </div>
  )
}

function Row({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-9 h-9 rounded-lg bg-gray-100 dark:bg-navy-800 flex items-center justify-center text-accent-500">
        <Icon size={16} />
      </div>
      <div>
        <div className="text-xs text-gray-400">{label}</div>
        <div className="text-sm font-medium capitalize">{value}</div>
      </div>
    </div>
  )
}
