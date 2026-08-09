import React, { useEffect, useState } from 'react'
import { FileText, Users, BookOpen, MessageSquare, CheckCircle2, XCircle, Gauge } from 'lucide-react'
import { getAdminStats } from '../../services/adminService'

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    getAdminStats().then(setStats).catch(() => {})
  }, [])

  if (!stats) {
    return <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">Loading admin stats...</div>
  }

  const cards = [
    { label: 'Total Documents', value: stats.documents.total, icon: FileText, color: 'from-blue-500 to-blue-700' },
    { label: 'Successfully Indexed', value: stats.documents.completed, icon: CheckCircle2, color: 'from-emerald-500 to-emerald-700' },
    { label: 'Failed Processing', value: stats.documents.failed, icon: XCircle, color: 'from-red-500 to-red-700' },
    { label: 'Students', value: stats.students, icon: Users, color: 'from-purple-500 to-purple-700' },
    { label: 'Subjects', value: stats.subjects, icon: BookOpen, color: 'from-amber-500 to-amber-700' },
    { label: 'Total Chats', value: stats.chats, icon: MessageSquare, color: 'from-cyan-500 to-cyan-700' },
  ]

  const evalData = stats.rag_evaluation

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-1">Admin Overview</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Usage statistics and RAG evaluation summary.</p>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {cards.map((c) => (
            <div key={c.label} className="rounded-2xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 p-5">
              <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${c.color} flex items-center justify-center text-white mb-3`}>
                <c.icon size={18} />
              </div>
              <div className="text-2xl font-bold">{c.value}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{c.label}</div>
            </div>
          ))}
        </div>

        <div className="rounded-2xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Gauge size={18} className="text-accent-500" />
            <h2 className="font-semibold">RAG Evaluation (lightweight)</h2>
          </div>
          <div className="grid sm:grid-cols-3 gap-4 mb-4">
            <Metric label="Questions Answered" value={evalData.total_questions_answered} />
            <Metric label="Grounded Answers" value={evalData.grounded_answers} />
            <Metric
              label="Grounded Rate"
              value={evalData.grounded_answer_rate !== null ? `${Math.round(evalData.grounded_answer_rate * 100)}%` : '—'}
            />
          </div>
          <p className="text-xs text-gray-400 leading-relaxed">{evalData.note}</p>
        </div>
      </div>
    </div>
  )
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl bg-gray-50 dark:bg-navy-800 p-4 text-center">
      <div className="text-xl font-bold">{value}</div>
      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{label}</div>
    </div>
  )
}
