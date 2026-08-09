import React, { useEffect, useState } from 'react'
import { Bookmark, Trash2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { listBookmarks, deleteBookmark } from '../services/bookmarkService'

export default function BookmarksPage() {
  const [bookmarks, setBookmarks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listBookmarks().then(setBookmarks).finally(() => setLoading(false))
  }, [])

  const handleDelete = async (id) => {
    await deleteBookmark(id)
    setBookmarks((prev) => prev.filter((b) => b.id !== id))
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-3xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-1">Bookmarks</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Answers you've saved for quick revision.</p>

        {loading ? (
          <p className="text-sm text-gray-400">Loading...</p>
        ) : bookmarks.length === 0 ? (
          <div className="text-center py-16">
            <Bookmark className="mx-auto text-gray-300 dark:text-navy-700 mb-3" size={32} />
            <p className="text-sm text-gray-400">No bookmarks yet. Save useful answers from a chat.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {bookmarks.map((b) => (
              <div key={b.id} className="rounded-2xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 p-5">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div>
                    <div className="text-sm font-semibold">{b.question}</div>
                    <div className="text-xs text-gray-400 mt-0.5">
                      {b.subject_name || 'General'} {b.unit_name ? `· ${b.unit_name}` : ''} · {new Date(b.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <button onClick={() => handleDelete(b.id)} className="text-gray-400 hover:text-red-500 transition-colors shrink-0">
                    <Trash2 size={16} />
                  </button>
                </div>
                <div className="prose-chat text-sm text-gray-700 dark:text-gray-300">
                  <ReactMarkdown>{b.answer}</ReactMarkdown>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
