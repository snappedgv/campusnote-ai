import React, { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Send, GraduationCap } from 'lucide-react'
import ChatMessage from '../components/ChatMessage.jsx'
import Selector from '../components/Selector.jsx'
import { listSubjects } from '../services/subjectService'
import { sendChatMessage, getChat } from '../services/chatService'

const EXAM_TYPES = [
  { value: 'CAT 1', label: 'CAT 1' },
  { value: 'CAT 2', label: 'CAT 2' },
  { value: 'Semester', label: 'Semester Exam' },
]
const MARKS = [2, 5, 10, 13, 15].map((m) => ({ value: String(m), label: `${m} Marks` }))

const STUDY_ACTIONS = [
  'Explain simpler',
  'Make it shorter',
  'Generate revision points',
  'Generate important keywords',
  'Create practice questions from this unit',
]

export default function ChatPage() {
  const { chatId } = useParams()
  const navigate = useNavigate()

  const [subjects, setSubjects] = useState([])
  const [subjectId, setSubjectId] = useState('')
  const [unitId, setUnitId] = useState('')
  const [examType, setExamType] = useState('')
  const [marks, setMarks] = useState('')

  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [currentChatId, setCurrentChatId] = useState(chatId || null)

  const bottomRef = useRef(null)

  useEffect(() => {
    listSubjects().then(setSubjects).catch(() => setSubjects([]))
  }, [])

  useEffect(() => {
    if (chatId) {
      getChat(chatId).then((chat) => {
        setCurrentChatId(chat.id)
        setSubjectId(chat.subject_id || '')
        setUnitId(chat.unit_id || '')
        setMessages(chat.messages.map((m) => ({ ...m, question: m.role === 'assistant' ? undefined : m.content })))
      }).catch(() => {})
    } else {
      setMessages([])
      setCurrentChatId(null)
    }
  }, [chatId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  const selectedSubject = subjects.find((s) => s.id === subjectId)
  const unitOptions = (selectedSubject?.units || []).map((u) => ({ value: u.id, label: u.name }))

  const send = async (text) => {
    const question = (text ?? input).trim()
    if (!question || sending) return
    setInput('')
    setSending(true)

    setMessages((prev) => [...prev, { role: 'user', content: question, id: `temp-${Date.now()}` }])

    try {
      const res = await sendChatMessage({
        chat_id: currentChatId,
        question,
        subject_id: subjectId || null,
        unit_id: unitId || null,
        exam_type: examType || null,
        marks: marks ? parseInt(marks) : null,
      })
      if (!currentChatId) {
        setCurrentChatId(res.chat_id)
        navigate(`/chat/${res.chat_id}`, { replace: true })
      }
      setMessages((prev) => [...prev, {
        id: res.message_id,
        role: 'assistant',
        content: res.answer,
        sources: res.sources,
        grounded: res.grounded,
        question_type: res.question_type,
        marks: res.marks,
        question,
      }])
    } catch (err) {
      setMessages((prev) => [...prev, {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: err?.response?.data?.detail || 'Something went wrong. Please try again.',
        sources: [],
        grounded: false,
      }])
    } finally {
      setSending(false)
    }
  }

  const handleStudyAction = (action) => {
    send(`${action} for the previous answer.`)
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Top selector bar */}
      <div className="border-b border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 px-6 py-3 flex flex-wrap items-center gap-2">
        <Selector label="Subject" value={subjectId} onChange={(v) => { setSubjectId(v); setUnitId('') }} options={subjects.map((s) => ({ value: s.id, label: s.name }))} />
        <Selector label="Unit" value={unitId} onChange={setUnitId} options={unitOptions} />
        <Selector label="Exam" value={examType} onChange={setExamType} options={EXAM_TYPES} />
        <Selector label="Marks" value={marks} onChange={setMarks} options={MARKS} />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-16">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-accent-500 to-blue-700 flex items-center justify-center text-white mx-auto mb-4">
                <GraduationCap size={26} />
              </div>
              <h2 className="text-lg font-semibold">Ask CampusNote AI</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 max-w-sm mx-auto">
                Select a subject and unit, then ask an exam question — answers are grounded strictly in your uploaded college notes.
              </p>
            </div>
          )}

          {messages.map((m) => (
            <ChatMessage key={m.id} message={m} subjectName={selectedSubject?.name} unitName={unitOptions.find((u) => u.value === unitId)?.label} />
          ))}

          {sending && (
            <div className="flex justify-start">
              <div className="bg-white dark:bg-navy-900 border border-gray-200 dark:border-navy-800 rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1.5">
                <span className="w-2 h-2 rounded-full bg-gray-400 typing-dot" />
                <span className="w-2 h-2 rounded-full bg-gray-400 typing-dot" />
                <span className="w-2 h-2 rounded-full bg-gray-400 typing-dot" />
              </div>
            </div>
          )}

          {messages.length > 0 && !sending && (
            <div className="flex flex-wrap gap-2 pt-2">
              {STUDY_ACTIONS.map((action) => (
                <button
                  key={action}
                  onClick={() => handleStudyAction(action)}
                  className="text-xs font-medium px-3 py-1.5 rounded-full border border-gray-200 dark:border-navy-700 text-gray-600 dark:text-gray-300 hover:border-accent-500 hover:text-accent-500 transition-colors"
                >
                  {action}
                </button>
              ))}
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input box */}
      <div className="border-t border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
            placeholder="Ask a question about your college notes..."
            rows={1}
            className="flex-1 resize-none px-4 py-3 rounded-2xl border border-gray-300 dark:border-navy-700 bg-gray-50 dark:bg-navy-800 text-sm focus:outline-none focus:ring-2 focus:ring-accent-500 max-h-32"
          />
          <button
            onClick={() => send()}
            disabled={sending || !input.trim()}
            className="w-11 h-11 shrink-0 rounded-2xl bg-accent-500 hover:bg-accent-600 disabled:opacity-50 text-white flex items-center justify-center transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
