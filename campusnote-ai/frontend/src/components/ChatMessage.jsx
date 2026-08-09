import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { FileText, HelpCircle, Bookmark, BookmarkCheck, AlertTriangle } from 'lucide-react'
import { createBookmark } from '../services/bookmarkService'

export default function ChatMessage({ message, subjectName, unitName }) {
  const isUser = message.role === 'user'
  const [showWhy, setShowWhy] = useState(false)
  const [bookmarked, setBookmarked] = useState(false)
  const [saving, setSaving] = useState(false)

  const handleBookmark = async () => {
    if (bookmarked || saving) return
    setSaving(true)
    try {
      await createBookmark({
        message_id: message.id,
        question: message.question || '',
        answer: message.content,
        subject_name: subjectName,
        unit_name: unitName,
        sources: message.sources,
      })
      setBookmarked(true)
    } catch {
      // silent fail is acceptable for a non-critical action; UI simply won't flip
    } finally {
      setSaving(false)
    }
  }

  if (isUser) {
    return (
      <div className="flex justify-end animate-slide-up">
        <div className="max-w-[80%] bg-accent-500 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm">
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start animate-slide-up">
      <div className="max-w-[85%] w-full">
        <div className="bg-white dark:bg-navy-900 border border-gray-200 dark:border-navy-800 rounded-2xl rounded-tl-sm px-4 py-3">
          {!message.grounded && (
            <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 text-xs font-medium mb-2 bg-amber-50 dark:bg-amber-500/10 rounded-lg px-2.5 py-1.5">
              <AlertTriangle size={13} /> Not grounded in uploaded notes
            </div>
          )}
          <div className="prose-chat text-sm text-gray-800 dark:text-gray-100">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          </div>

          {message.sources && message.sources.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-100 dark:border-navy-800">
              <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1.5">
                📚 Sources
              </div>
              <div className="space-y-1.5">
                {message.sources.map((s, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-navy-800 rounded-lg px-2.5 py-1.5">
                    <FileText size={12} className="shrink-0 text-accent-500" />
                    <span className="truncate">{s.document}{s.page ? ` — Page ${s.page}` : ''}</span>
                    {s.unit && <span className="text-gray-400 shrink-0">· {s.unit}</span>}
                    <span className="ml-auto shrink-0 text-gray-400">{Math.round(s.relevance * 100)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-3 pt-2 flex items-center gap-3 border-t border-gray-100 dark:border-navy-800">
            {message.sources && message.sources.length > 0 && (
              <button
                onClick={() => setShowWhy((v) => !v)}
                className="flex items-center gap-1.5 text-xs font-medium text-gray-500 dark:text-gray-400 hover:text-accent-500 transition-colors"
              >
                <HelpCircle size={13} /> Why this answer?
              </button>
            )}
            <button
              onClick={handleBookmark}
              disabled={saving}
              className="flex items-center gap-1.5 text-xs font-medium text-gray-500 dark:text-gray-400 hover:text-accent-500 transition-colors ml-auto"
            >
              {bookmarked ? <BookmarkCheck size={13} className="text-accent-500" /> : <Bookmark size={13} />}
              {bookmarked ? 'Bookmarked' : 'Bookmark'}
            </button>
          </div>

          {showWhy && (
            <div className="mt-3 space-y-2 animate-fade-in">
              {message.sources.map((s, i) => (
                <div key={i} className="rounded-xl bg-gray-50 dark:bg-navy-800 p-3 text-xs">
                  <div className="font-semibold text-gray-700 dark:text-gray-200 mb-1">
                    {s.document}{s.page ? ` — Page ${s.page}` : ''}
                  </div>
                  <div className="text-gray-500 dark:text-gray-400 mb-1">
                    Relevance score: {Math.round(s.relevance * 100)}%
                  </div>
                  <div className="text-gray-600 dark:text-gray-300 italic">"{s.excerpt}"</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
