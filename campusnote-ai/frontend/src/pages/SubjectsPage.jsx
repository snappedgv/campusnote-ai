import React, { useEffect, useState } from 'react'
import { Search, BookOpen, FileText } from 'lucide-react'
import { listSubjects } from '../services/subjectService'
import { semanticSearch } from '../services/adminService'

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState([])
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    listSubjects().then(setSubjects).catch(() => setSubjects([]))
  }, [])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setSearching(true)
    try {
      const res = await semanticSearch(query)
      setResults(res.results)
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-1">Subjects</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Browse subjects and units, or search your notes directly.</p>

        <form onSubmit={handleSearch} className="relative mb-8">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search notes... e.g. normalization, deadlock, TCP congestion control"
            className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-300 dark:border-navy-700 bg-white dark:bg-navy-900 text-sm focus:outline-none focus:ring-2 focus:ring-accent-500"
          />
        </form>

        {results && (
          <div className="mb-8">
            <h2 className="text-sm font-semibold mb-3">Search results</h2>
            {searching ? (
              <p className="text-sm text-gray-400">Searching...</p>
            ) : results.length === 0 ? (
              <p className="text-sm text-gray-400">No matching notes found.</p>
            ) : (
              <div className="space-y-2">
                {results.map((r) => (
                  <div key={r.chunk_id} className="rounded-xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 p-4">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                      <FileText size={12} className="text-accent-500" />
                      {r.document}{r.page ? ` — Page ${r.page}` : ''}
                      <span className="ml-auto">{Math.round(r.relevance * 100)}% match</span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-3">{r.text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <h2 className="text-sm font-semibold mb-3">All subjects</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {subjects.map((s) => (
            <div key={s.id} className="rounded-2xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 p-5">
              <div className="flex items-center gap-2 mb-2">
                <BookOpen size={16} className="text-accent-500" />
                <span className="font-semibold text-sm">{s.name}</span>
                {s.code && <span className="text-xs text-gray-400">({s.code})</span>}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {s.units.map((u) => (
                  <span key={u.id} className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-navy-800 text-gray-600 dark:text-gray-300">
                    {u.name}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
