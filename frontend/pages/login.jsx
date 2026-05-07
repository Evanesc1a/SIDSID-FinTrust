import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/authcontext'
import { Shield, Eye, EyeOff, Lock, Mail, AlertCircle } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email || !password) { setError('Completa todos los campos'); return }
    setLoading(true)
    setError('')
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Credenciales inválidas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', background: '#060b14',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 24, position: 'relative', overflow: 'hidden',
    }}>
      {/* Grid background */}
      <div style={{
        position:'absolute', inset:0, opacity:0.4,
        backgroundImage: 'linear-gradient(rgba(30,58,95,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(30,58,95,0.4) 1px, transparent 1px)',
        backgroundSize: '48px 48px',
      }} />

      {/* Glow orbs */}
      <div style={{ position:'absolute', top:'15%', left:'10%', width:300, height:300, background:'radial-gradient(circle, rgba(29,78,216,0.12) 0%, transparent 70%)', pointerEvents:'none' }} />
      <div style={{ position:'absolute', bottom:'15%', right:'10%', width:250, height:250, background:'radial-gradient(circle, rgba(8,145,178,0.1) 0%, transparent 70%)', pointerEvents:'none' }} />

      <div style={{ position:'relative', width:'100%', maxWidth:420 }}>
        {/* Header */}
        <div style={{ textAlign:'center', marginBottom:40 }}>
          <div style={{
            display:'inline-flex', alignItems:'center', justifyContent:'center',
            width:60, height:60,
            background:'linear-gradient(135deg, #1d4ed8, #0891b2)',
            borderRadius:16, marginBottom:20,
            boxShadow:'0 0 32px rgba(29,78,216,0.35)',
          }}>
            <Shield size={28} color="white" />
          </div>
          <h1 style={{
            fontFamily:'Space Grotesk, sans-serif', fontSize:'1.6rem',
            fontWeight:700, color:'#e2e8f0', margin:'0 0 6px',
          }}>
            SIDSID
          </h1>
          <p style={{ color:'#475569', fontSize:'0.8rem', margin:0, fontFamily:'JetBrains Mono, monospace', letterSpacing:'0.1em' }}>
            FINTRUST DIGITAL SERVICES — PANEL DE SEGURIDAD
          </p>
        </div>

        {/* Card */}
        <div style={{
          background:'#0a1628', border:'1px solid #1e3a5f',
          borderRadius:16, padding:'32px 36px',
          boxShadow:'0 24px 60px rgba(0,0,0,0.5)',
        }}>
          <h2 style={{ fontFamily:'Space Grotesk, sans-serif', fontSize:'1rem', fontWeight:600, color:'#94a3b8', margin:'0 0 24px', textTransform:'uppercase', letterSpacing:'0.08em' }}>
            Iniciar sesión
          </h2>

          <form onSubmit={handleSubmit} style={{ display:'flex', flexDirection:'column', gap:16 }}>
            {/* Email */}
            <div>
              <label style={{ display:'block', fontSize:'0.75rem', color:'#64748b', marginBottom:6, fontFamily:'JetBrains Mono, monospace', textTransform:'uppercase', letterSpacing:'0.08em' }}>
                Email
              </label>
              <div style={{ position:'relative' }}>
                <Mail size={15} style={{ position:'absolute', left:14, top:'50%', transform:'translateY(-50%)', color:'#475569' }} />
                <input
                  type="email" value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="analista@fintrust.co"
                  style={{
                    width:'100%', padding:'11px 14px 11px 40px',
                    background:'#060b14', border:'1px solid #1e3a5f',
                    borderRadius:8, color:'#e2e8f0', fontSize:'0.875rem',
                    outline:'none', boxSizing:'border-box',
                    fontFamily:'DM Sans, sans-serif',
                    transition:'border-color 0.15s',
                  }}
                  onFocus={e => e.target.style.borderColor = '#3b82f6'}
                  onBlur={e => e.target.style.borderColor = '#1e3a5f'}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label style={{ display:'block', fontSize:'0.75rem', color:'#64748b', marginBottom:6, fontFamily:'JetBrains Mono, monospace', textTransform:'uppercase', letterSpacing:'0.08em' }}>
                Contraseña
              </label>
              <div style={{ position:'relative' }}>
                <Lock size={15} style={{ position:'absolute', left:14, top:'50%', transform:'translateY(-50%)', color:'#475569' }} />
                <input
                  type={showPass ? 'text' : 'password'} value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••"
                  style={{
                    width:'100%', padding:'11px 44px 11px 40px',
                    background:'#060b14', border:'1px solid #1e3a5f',
                    borderRadius:8, color:'#e2e8f0', fontSize:'0.875rem',
                    outline:'none', boxSizing:'border-box',
                    fontFamily:'DM Sans, sans-serif',
                    transition:'border-color 0.15s',
                  }}
                  onFocus={e => e.target.style.borderColor = '#3b82f6'}
                  onBlur={e => e.target.style.borderColor = '#1e3a5f'}
                />
                <button type="button" onClick={() => setShowPass(!showPass)} style={{
                  position:'absolute', right:12, top:'50%', transform:'translateY(-50%)',
                  background:'none', border:'none', cursor:'pointer', color:'#475569', padding:2,
                }}>
                  {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div style={{
                display:'flex', alignItems:'center', gap:8,
                background:'rgba(239,68,68,0.1)', border:'1px solid rgba(239,68,68,0.3)',
                borderRadius:8, padding:'10px 14px', color:'#ef4444', fontSize:'0.8rem',
              }}>
                <AlertCircle size={14} />
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              type="submit" disabled={loading}
              style={{
                padding:'12px', background: loading ? '#1e3a5f' : 'linear-gradient(135deg, #1d4ed8, #0891b2)',
                border:'none', borderRadius:8, color:'white',
                fontSize:'0.875rem', fontWeight:600, cursor: loading ? 'not-allowed' : 'pointer',
                fontFamily:'Space Grotesk, sans-serif', letterSpacing:'0.04em',
                transition:'opacity 0.15s', opacity: loading ? 0.7 : 1,
                display:'flex', alignItems:'center', justifyContent:'center', gap:8,
              }}
            >
              {loading ? (
                <>
                  <div style={{ width:14, height:14, border:'2px solid rgba(255,255,255,0.3)', borderTopColor:'white', borderRadius:'50%', animation:'spin 0.7s linear infinite' }} />
                  Autenticando...
                </>
              ) : 'Acceder al sistema'}
            </button>
          </form>

          {/* Demo credentials */}
          <div style={{ marginTop:24, padding:'14px', background:'#060b14', borderRadius:8, border:'1px solid #1e3a5f' }}>
            <p style={{ color:'#475569', fontSize:'0.7rem', margin:'0 0 8px', fontFamily:'JetBrains Mono, monospace', textTransform:'uppercase', letterSpacing:'0.08em' }}>
              Credenciales de demo
            </p>
            <div style={{ display:'flex', flexDirection:'column', gap:3 }}>
              {[
                ['Admin', 'admin@fintrust.co', 'sidsid123'],
                ['Analista', 'analista@fintrust.co', 'sidsid123'],
              ].map(([rol, em, pw]) => (
                <div key={rol} style={{ display:'flex', gap:8, alignItems:'center' }}>
                  <span style={{ color:'#475569', fontSize:'0.7rem', width:50, fontFamily:'JetBrains Mono, monospace' }}>{rol}</span>
                  <button onClick={() => { setEmail(em); setPassword(pw) }}
                    style={{
                      background:'none', border:'none', cursor:'pointer',
                      color:'#3b82f6', fontSize:'0.72rem', padding:0,
                      fontFamily:'JetBrains Mono, monospace', textDecoration:'underline',
                    }}>
                    {em}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } } input::placeholder { color: #334155; }`}</style>
    </div>
  )
}
