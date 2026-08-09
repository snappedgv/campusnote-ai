import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { MessageSquare, Trash2, Search } from 'lucide-react'
import { listChats, deleteChat } from '../services/chatService'

export default function HistoryPage() {
  const [chats, setChats] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    listChats().then(setChats).finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleDelete = async (id, e) => {
    e.preventDefault()
    e.stopPropagation()
    await deleteChat(id)
    setChats((prev) => prev.filter((c) => c.id !== id))
  }

  const filtered = chats.filter((c) => c.title.toLowerCase().includes(query.toLowerCase()))

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-3xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-1">Chat History</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Search and revisit your past questions.</p>

        <div className="relative mb-5">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search chat history..."
            className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-300 dark:border-navy-700 bg-white dark:bg-navy-900 text-sm focus:outline-none focus:ring-2 focus:ring-accent-500"
          />
        </div>

        {loading ? (
          <p className="text-sm text-gray-400">Loading...</p>
        ) : filtered.length === 0 ? (
          <p className="text-sm text-gray-400">No chats found.</p>
        ) : (
          <div className="space-y-2">
            {filtered.map((c) => (
              <Link
                key={c.id}
                to={`/chat/${c.id}`}
                className="flex items-center gap-3 p-4 rounded-xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 hover:border-accent-500 transition-colors group"
              >
                <MessageSquare size={16} className="text-accent-500 shrink-0" />
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium truncate">{c.title}</div>
                  <div className="text-xs text-gray-400">{new Date(c.updated_at).toLocaleString()}</div>
                </div>
                <button
                  onClick={(e) => handleDelete(c.id, e)}
                  className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity"
                >
                  <Trash2 size={16} />
                </button>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
