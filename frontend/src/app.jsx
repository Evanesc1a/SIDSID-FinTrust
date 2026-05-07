import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AuthProvider } from '../context/authcontext'
import ProtectedRoute from '../components/protectedroute'
import Navbar from '../components/navbar'
import Login from '../pages/login'
import Dashboard from '../pages/dashboard'
import Alertas from '../pages/alertas'
import DetalleAlerta from '../pages/detalle_alerta'
import Usuarios from '../pages/usuarios'
import { alertasService } from '../services/alertasservice'
import { useAuth } from '../context/authcontext'

function AppLayout() {
  const { usuario } = useAuth()
  const location = useLocation()
  const [alertasNuevas, setAlertasNuevas] = useState(0)
  const isLogin = location.pathname === '/login'

  useEffect(() => {
    if (!usuario) return
    const fetch = () => {
      alertasService.resumen().then(r => setAlertasNuevas(r.data.total_nuevas)).catch(() => {})
    }
    fetch()
    const id = setInterval(fetch, 30000)
    return () => clearInterval(id)
  }, [usuario])

  return (
    <div style={{ minHeight:'100vh', background:'#060b14' }}>
      {!isLogin && usuario && <Navbar alertasNuevas={alertasNuevas} />}
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/alertas" element={<ProtectedRoute><Alertas /></ProtectedRoute>} />
        <Route path="/alertas/:id" element={<ProtectedRoute><DetalleAlerta /></ProtectedRoute>} />
        <Route path="/usuarios" element={<ProtectedRoute><Usuarios /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppLayout />
      </AuthProvider>
    </BrowserRouter>
  )
}
