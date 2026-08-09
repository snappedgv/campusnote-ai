import React, { useEffect, useState } from 'react'
import { Upload, RefreshCw, Trash2, FileText, X } from 'lucide-react'
import { listDocuments, uploadDocument, deleteDocument, reindexDocument } from '../../services/documentService'
import { listSubjects } from '../../services/subjectService'

const STATUS_STYLES = {
  pending: 'bg-gray-100 text-gray-600 dark:bg-navy-800 dark:text-gray-300',
  processing: 'bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400',
  completed: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400',
  failed: 'bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400',
}

export default function AdminDocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [subjects, setSubjects] = useState([])
  const [showUpload, setShowUpload] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = () => {
    setLoading(true)
    listDocuments().then(setDocuments).finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    listSubjects().then(setSubjects).catch(() => setSubjects([]))
  }, [])

  // Poll while any document is pending/processing, so status updates without manual refresh
  useEffect(() => {
    const hasActive = documents.some((d) => ['pending', 'processing'].includes(d.processing_status))
    if (!hasActive) return
    const interval = setInterval(load, 3000)
    return () => clearInterval(interval)
  }, [documents])

  const handleDelete = async (id) => {
    await deleteDocument(id)
    setDocuments((prev) => prev.filter((d) => d.id !== id))
  }

  const handleReindex = async (id) => {
    await reindexDocument(id)
    load()
  }

  const subjectName = (id) => subjects.find((s) => s.id === id)?.name || '—'
  const unitName = (subjectId, unitId) => {
    const subject = subjects.find((s) => s.id === subjectId)
    return subject?.units.find((u) => u.id === unitId)?.name || '—'
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Documents</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Upload and manage college notes for the RAG pipeline.</p>
          </div>
          <button
            onClick={() => setShowUpload(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-accent-500 hover:bg-accent-600 text-white text-sm font-semibold transition-colors"
          >
            <Upload size={16} /> Upload Document
          </button>
        </div>

        {error && <div className="mb-4 text-sm text-red-600 bg-red-50 dark:bg-red-500/10 rounded-lg px-3 py-2">{error}</div>}

        <div className="rounded-2xl border border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 dark:bg-navy-800 text-xs text-gray-500 dark:text-gray-400">
              <tr>
                <th className="text-left px-4 py-3 font-medium">File Name</th>
                <th className="text-left px-4 py-3 font-medium">Subject</th>
                <th className="text-left px-4 py-3 font-medium">Unit</th>
                <th className="text-left px-4 py-3 font-medium">Source</th>
                <th className="text-left px-4 py-3 font-medium">Pages</th>
                <th className="text-left px-4 py-3 font-medium">Status</th>
                <th className="text-left px-4 py-3 font-medium">Uploaded</th>
                <th className="text-right px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={8} className="text-center py-8 text-gray-400">Loading...</td></tr>
              ) : documents.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-8 text-gray-400">No documents uploaded yet.</td></tr>
              ) : (
                documents.map((d) => (
                  <tr key={d.id} className="border-t border-gray-100 dark:border-navy-800">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <FileText size={14} className="text-accent-500 shrink-0" />
                        <span className="truncate max-w-[220px]">{d.filename}</span>
                      </div>
                      {d.processing_error && <div className="text-xs text-red-500 mt-1 max-w-[260px]">{d.processing_error}</div>}
                    </td>
                    <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{subjectName(d.subject_id)}</td>
                    <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{unitName(d.subject_id, d.unit_id)}</td>
                    <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{d.source || '—'}</td>
                    <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{d.page_count ?? '—'}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-medium px-2 py-1 rounded-full ${STATUS_STYLES[d.processing_status]}`}>
                        {d.processing_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{new Date(d.uploaded_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => handleReindex(d.id)} title="Re-index" className="text-gray-400 hover:text-accent-500 transition-colors">
                          <RefreshCw size={15} />
                        </button>
                        <button onClick={() => handleDelete(d.id)} title="Delete" className="text-gray-400 hover:text-red-500 transition-colors">
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showUpload && (
        <UploadModal
          subjects={subjects}
          onClose={() => setShowUpload(false)}
          onUploaded={() => { setShowUpload(false); load() }}
          onError={setError}
        />
      )}
    </div>
  )
}

function UploadModal({ subjects, onClose, onUploaded, onError }) {
  const [file, setFile] = useState(null)
  const [subjectId, setSubjectId] = useState('')
  const [unitId, setUnitId] = useState('')
  const [topic, setTopic] = useState('')
  const [department, setDepartment] = useState('')
  const [semester, setSemester] = useState('')
  const [academicYear, setAcademicYear] = useState('')
  const [faculty, setFaculty] = useState('')
  const [source, setSource] = useState('Manual Upload')
  const [uploading, setUploading] = useState(false)

  const selectedSubject = subjects.find((s) => s.id === subjectId)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return
    setUploading(true)
    onError('')
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (subjectId) formData.append('subject_id', subjectId)
      if (unitId) formData.append('unit_id', unitId)
      if (topic) formData.append('topic', topic)
      if (department) formData.append('department', department)
      if (semester) formData.append('semester', semester)
      if (academicYear) formData.append('academic_year', academicYear)
      if (faculty) formData.append('faculty', faculty)
      formData.append('source', source)
      await uploadDocument(formData)
      onUploaded()
    } catch (err) {
      onError(err?.response?.data?.detail || 'Upload failed.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
      <div className="bg-white dark:bg-navy-900 rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-lg">Upload Document</h2>
          <button onClick={onClose}><X size={18} className="text-gray-400" /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">File (PDF, DOCX, PPTX, TXT)</label>
            <input type="file" accept=".pdf,.docx,.pptx,.txt" required onChange={(e) => setFile(e.target.files[0])} className="text-sm w-full" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <SelectField label="Subject" value={subjectId} onChange={(v) => { setSubjectId(v); setUnitId('') }} options={subjects.map((s) => ({ value: s.id, label: s.name }))} />
            <SelectField label="Unit" value={unitId} onChange={setUnitId} options={(selectedSubject?.units || []).map((u) => ({ value: u.id, label: u.name }))} />
          </div>
          <TextField label="Topic" value={topic} onChange={setTopic} placeholder="e.g. Normalization" />
          <div className="grid grid-cols-2 gap-3">
            <TextField label="Department" value={department} onChange={setDepartment} placeholder="AI & Data Science" />
            <TextField label="Semester" value={semester} onChange={setSemester} placeholder="4" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <TextField label="Academic Year" value={academicYear} onChange={setAcademicYear} placeholder="2025-26" />
            <TextField label="Faculty" value={faculty} onChange={setFaculty} placeholder="Faculty name" />
          </div>
          <TextField label="Source" value={source} onChange={setSource} placeholder="Manual Upload / LMS" />

          <button
            type="submit"
            disabled={uploading || !file}
            className="w-full mt-2 py-2.5 rounded-xl bg-accent-500 hover:bg-accent-600 disabled:opacity-60 text-white font-semibold text-sm transition-colors"
          >
            {uploading ? 'Uploading...' : 'Upload & Process'}
          </button>
        </form>
      </div>
    </div>
  )
}

function TextField({ label, value, onChange, placeholder }) {
  return (
    <div>
      <label className="text-xs font-medium text-gray-500 mb-1 block">{label}</label>
      <input
        value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder}
        className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-navy-700 bg-white dark:bg-navy-800 text-sm focus:outline-none focus:ring-2 focus:ring-accent-500"
      />
    </div>
  )
}

function SelectField({ label, value, onChange, options }) {
  return (
    <div>
      <label className="text-xs font-medium text-gray-500 mb-1 block">{label}</label>
      <select
        value={value} onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-navy-700 bg-white dark:bg-navy-800 text-sm focus:outline-none focus:ring-2 focus:ring-accent-500"
      >
        <option value="">None</option>
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  )
}
