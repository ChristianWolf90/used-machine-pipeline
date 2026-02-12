import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { CssBaseline } from '@mui/material'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import MachineListPage from './pages/MachineListPage'
import MachineDetailPage from './pages/MachineDetailPage'
import DashboardPage from './pages/DashboardPage'
import { getSession } from './auth/auth'

function PrivateRoute({ children }: { children: JSX.Element }) {
  return getSession() ? children : <Navigate to="/login" replace />
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <CssBaseline />
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          element={<PrivateRoute><Layout /></PrivateRoute>}
        >
          <Route path="/machines" element={<MachineListPage />} />
          <Route path="/machines/:id" element={<MachineDetailPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/machines" replace />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
