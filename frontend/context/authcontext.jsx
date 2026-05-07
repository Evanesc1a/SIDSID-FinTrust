import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('sidsid_token')
    const userData = localStorage.getItem('sidsid_usuario')
    if (token && userData) {
      setUsuario(JSON.parse(userData))
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password })
    const { access_token, usuario: user } = response.data

    // Guardar ANTES de cualquier navegación
    localStorage.setItem('sidsid_token', access_token)
    localStorage.setItem('sidsid_usuario', JSON.stringify(user))

    setUsuario(user)
    return user
  }

  const logout = () => {
    localStorage.removeItem('sidsid_token')
    localStorage.removeItem('sidsid_usuario')
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ usuario, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}