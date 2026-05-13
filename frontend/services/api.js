import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

// Inyecta el token en CADA request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sidsid_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Redirige a login si el token expiró o es inválido
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('sidsid_token')
      localStorage.removeItem('sidsid_usuario')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api