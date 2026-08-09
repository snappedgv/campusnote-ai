import React from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  MessageSquarePlus, History, Bookmark, BookOpen, User, LogOut,
  Sun, Moon, ShieldCheck, LayoutDashboard, GraduationCap,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext.jsx'
import { useTheme } from '../context/ThemeContext.jsx'

const studentNav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/chat', label: 'New Chat', icon: MessageSquarePlus },
  { to: '/history', label: 'Chat History', icon: History },
  { to: '/subjects', label: 'Subjects', icon: BookOpen },
  { to: '/bookmarks', label: 'Bookmarks', icon: Bookmark },
]

const adminNav = [
  { to: '/admin', label: 'Admin Overview', icon: ShieldCheck },
  { to: '/admin/documents', label: 'Documents', icon: BookOpen },
  { to: '/admin/subjects', label: 'Subjects & Units', icon: GraduationCap },
]

export default function AppLayout() {
  const { user, logout, isAdmin } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()

  return (
    <div className="h-screen flex bg-gray-50 dark:bg-navy-950 text-gray-900 dark:text-gray-100">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 hidden md:flex flex-col border-r border-gray-200 dark:border-navy-800 bg-white dark:bg-navy-900">
        <div className="px-5 py-5 flex items-center gap-2 border-b border-gray-200 dark:border-navy-800">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-500 to-blue-700 flex items-center justify-center text-white font-bold text-sm">C</div>
          <div>
            <div className="font-bold text-sm leading-tight">CampusNote AI</div>
            <div className="text-[11px] text-gray-500 dark:text-gray-400 leading-tight">Study Assistant</div>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {(isAdmin ? adminNav : studentNav).map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-accent-500/10 text-accent-600 dark:text-accent-400'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-navy-800'
                }`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-gray-200 dark:border-navy-800 space-y-1">
          <button
            onClick={toggleTheme}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-navy-800 transition-colors"
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            {theme === 'dark' ? 'Light mode' : 'Dark mode'}
          </button>
          <NavLink
            to="/profile"
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-navy-800 transition-colors"
          >
            <User size={18} />
            {user?.name || 'Profile'}
          </NavLink>
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 flex flex-col">
        <Outlet />
      </main>
    </div>
  )
}
