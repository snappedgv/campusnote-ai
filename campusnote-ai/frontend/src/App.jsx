import React from 'react'
import { Routes, Route } from 'react-router-dom'

import LandingPage from './pages/LandingPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import ChatPage from './pages/ChatPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import BookmarksPage from './pages/BookmarksPage.jsx'
import SubjectsPage from './pages/SubjectsPage.jsx'
import ProfilePage from './pages/ProfilePage.jsx'

import AdminDashboardPage from './pages/admin/AdminDashboardPage.jsx'
import AdminDocumentsPage from './pages/admin/AdminDocumentsPage.jsx'
import AdminSubjectsPage from './pages/admin/AdminSubjectsPage.jsx'

import { ProtectedRoute, AdminRoute } from './components/ProtectedRoute.jsx'
import AppLayout from './layouts/AppLayout.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:chatId" element={<ChatPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/bookmarks" element={<BookmarksPage />} />
        <Route path="/subjects" element={<SubjectsPage />} />
        <Route path="/profile" element={<ProfilePage />} />

        <Route path="/admin" element={<AdminRoute><AdminDashboardPage /></AdminRoute>} />
        <Route path="/admin/documents" element={<AdminRoute><AdminDocumentsPage /></AdminRoute>} />
        <Route path="/admin/subjects" element={<AdminRoute><AdminSubjectsPage /></AdminRoute>} />
      </Route>

      <Route path="*" element={<LandingPage />} />
    </Routes>
  )
}
