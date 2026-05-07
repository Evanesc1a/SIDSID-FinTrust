import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/authcontext'

export default function ProtectedRoute({ children }) {
  const { usuario, loading } = useAuth()

  if (loading) {
    return (
      <div style={{
        minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center',
        background:'#060b14',
      }}>
        <div style={{ textAlign:'center' }}>
          <div style={{
            width:40, height:40, border:'2px solid #1e3a5f',
            borderTopColor:'#3b82f6', borderRadius:'50%',
            animation:'spin 0.8s linear infinite', margin:'0 auto 12px',
          }} />
          <span style={{ color:'#475569', fontSize:'0.8rem', fontFamily:'JetBrains Mono, monospace' }}>
            CARGANDO...
          </span>
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    )
  }

  if (!usuario) return <Navigate to="/login" replace />
  return children
}
