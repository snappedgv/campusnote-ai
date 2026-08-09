import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, FileText, MessageSquare, Bookmark, MessageSquarePlus } from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import { listSubjects } from '../services/subjectService'
import { listDocuments } from '../services/documentService'
import { listChats } from '../services/chatService'
import { listBookmarks } from '../services/bookmarkService'

export default function DashboardPage() {
  const { user } = useAuth()
  const [subjects, setSubjects] = useState([])
  const [documentsCount, setDocumentsCount] = useState(0)
  const [chats, setChats] = useState([])
  const [bookmarksCount, setBookmarksCount] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      try {
        const [subj, docs, chatList, bms] = await Promise.all([
          listSubjects(),
          listDocuments().catch(() => []),
          listChats(),
          listBookmarks(),
        ])
        setSubjects(subj)
        setDocumentsCount(docs.length)
        setChats(chatList)
        setBookmarksCount(bms.length)
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const cards = [
    { label: 'Subjects', value: subjects.length, icon: BookOpen, color: 'from-blue-500 to-blue-700' },
    { label: 'Documents Available', value: documentsCount, icon: FileText, color: 'from-emerald-500 to-emerald-700' },
    { label: 'Questions Asked', value: chats.length, icon: MessageSquare, color: 'from-purple-500 to-purple-700' },
    { label: 'Bookmarked Answers', value: bookmarksCount, icon: Bookmark, color: 'from-amber-500 to-amber-700' },
  ]

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Welcome back, {user?.name?.split(' ')[0]} 👋</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {user?.semester ? `Semester ${user.semester}` : 'Ready to study smarter?'}
            </p>
          </div>
          <Link to="/chat" className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-accent-500 hover:bg-accent-600 text-white text-sm font-semibold transition-colors">
            <MessageSquarePlus size={16} /> New Chat
          </Link>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {cards.map((c) => (
            <div key={c.label} className="rounded-2xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 p-5">
              <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${c.color} flex items-center justify-center text-white mb-3`}>
                <c.icon size={18} />
              </div>
              <div className="text-2xl font-bold">{loading ? '—' : c.value}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{c.label}</div>
            </div>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <div className="rounded-2xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 p-5">
            <h2 className="font-semibold mb-3">Recent Questions</h2>
            {chats.length === 0 ? (
              <p className="text-sm text-gray-400">No chats yet. Start your first one!</p>
            ) : (
              <ul className="space-y-2">
                {chats.slice(0, 5).map((c) => (
                  <li key={c.id}>
                    <Link to={`/chat/${c.id}`} className="text-sm text-gray-700 dark:text-gray-300 hover:text-accent-500 transition-colors block truncate">
                      {c.title}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="rounded-2xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 p-5">
            <h2 className="font-semibold mb-3">Your Subjects</h2>
            {subjects.length === 0 ? (
              <p className="text-sm text-gray-400">No subjects available yet. Ask your admin to add them.</p>
            ) : (
              <ul className="space-y-2">
                {subjects.slice(0, 6).map((s) => (
                  <li key={s.id} className="text-sm text-gray-700 dark:text-gray-300 flex items-center justify-between">
                    <span>{s.name}</span>
                    <span className="text-xs text-gray-400">{s.code}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
