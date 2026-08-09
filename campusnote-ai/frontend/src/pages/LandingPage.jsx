import React from 'react'
import { Link } from 'react-router-dom'
import { GraduationCap, CheckCircle2, BookOpen, FileText, Target, Shield } from 'lucide-react'

const features = [
  { icon: CheckCircle2, text: 'Answers grounded in your actual college notes' },
  { icon: BookOpen, text: 'Subject, semester and unit filtering' },
  { icon: Target, text: 'Exam-oriented CAT 1 / CAT 2 / Semester answers' },
  { icon: FileText, text: 'Every answer cites the source document and page' },
  { icon: GraduationCap, text: '2 / 5 / 10 / 13 / 15 mark answer formats' },
  { icon: Shield, text: 'Secure student & admin login with JWT auth' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-navy-950 text-white">
      <header className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent-500 to-blue-700 flex items-center justify-center font-bold">C</div>
          <span className="font-bold text-lg">CampusNote AI</span>
        </div>
        <div className="flex gap-3">
          <Link to="/login" className="px-4 py-2 rounded-lg text-sm font-medium text-gray-200 hover:bg-navy-800 transition-colors">Login</Link>
          <Link to="/register" className="px-4 py-2 rounded-lg text-sm font-medium bg-accent-500 hover:bg-accent-600 transition-colors">Get Started</Link>
        </div>
      </header>

      <section className="max-w-4xl mx-auto px-6 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-navy-800 text-accent-400 text-xs font-medium mb-6">
          Retrieval-Augmented Generation · Built for exams
        </div>
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 bg-gradient-to-br from-white to-gray-400 bg-clip-text text-transparent">
          CampusNote AI
        </h1>
        <p className="text-xl md:text-2xl font-medium text-gray-300 mb-4">
          Your College Notes. Your Syllabus. Your Exam Assistant.
        </p>
        <p className="text-gray-400 max-w-2xl mx-auto mb-10">
          Unlike general AI chatbots, CampusNote AI answers strictly from your own
          college's uploaded notes — matching your faculty's terminology, syllabus,
          and units, with page-level source citations for every answer.
        </p>
        <div className="flex items-center justify-center gap-4">
          <Link to="/register" className="px-6 py-3 rounded-xl bg-accent-500 hover:bg-accent-600 font-semibold transition-colors">
            Get Started
          </Link>
          <Link to="/login" className="px-6 py-3 rounded-xl border border-navy-700 hover:bg-navy-800 font-semibold transition-colors">
            Login
          </Link>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-6 pb-24">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f, i) => (
            <div key={i} className="flex items-start gap-3 p-5 rounded-2xl bg-navy-900 border border-navy-800">
              <f.icon className="text-accent-400 shrink-0 mt-0.5" size={20} />
              <span className="text-sm text-gray-200">{f.text}</span>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-navy-800 py-8 text-center text-sm text-gray-500">
        CampusNote AI — a RAG-grounded study assistant built on your own college materials.
      </footer>
    </div>
  )
}
