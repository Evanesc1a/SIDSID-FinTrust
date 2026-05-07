import React, { useState, useEffect } from 'react'
import api from '../services/api'
import NivelBadge from '../components/nivelbadge'
import { Users, ShieldOff, ShieldCheck, Search, RefreshCw, User } from 'lucide-react'

function timeStr(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-CO', { year:'numeric', month:'short', day:'numeric' })
}

export default function Usuarios() {
  const [usuarios, setUsuarios] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [actionLoading, setActionLoading] = useState({})

  const cargar = async () => {
    setLoading(true)
    try {
      const res = await api.get('/usuarios')
      setUsuarios(res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { cargar() }, [])

  const toggleBloqueo = async (u) => {
    setActionLoading(prev => ({ ...prev, [u.id]: true }))
    try {
      const endpoint = u.estado === 'BLOQUEADA' ? `/usuarios/${u.id}/desbloquear` : `/usuarios/${u.id}/bloquear`
      await api.post(endpoint)
      await cargar()
    } finally {
      setActionLoading(prev => ({ ...prev, [u.id]: false }))
    }
  }

  const filtrados = usuarios.filter(u =>
    !search ||
    u.nombre?.toLowerCase().includes(search.toLowerCase()) ||
    u.email?.toLowerCase().includes(search.toLowerCase())
  )

  const activos = usuarios.filter(u => u.estado === 'ACTIVA').length
  const bloqueados = usuarios.filter(u => u.estado === 'BLOQUEADA').length

  return (
    <div style={{ padding:'28px 32px', maxWidth:1200, margin:'0 auto' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:28 }}>
        <div>
          <h1 style={{ fontFamily:'Space Grotesk, sans-serif', fontSize:'1.5rem', fontWeight:700, color:'#e2e8f0', margin:0 }}>
            Gestión de Usuarios
          </h1>
          <p style={{ color:'#475569', fontSize:'0.8rem', margin:'4px 0 0', fontFamily:'JetBrains Mono, monospace' }}>
            {activos} activos · {bloqueados} bloqueados
          </p>
        </div>
        <button onClick={cargar} style={{
          background:'#0a1628', border:'1px solid #1e3a5f', borderRadius:8,
          padding:'8px 16px', cursor:'pointer', color:'#64748b',
          display:'flex', alignItems:'center', gap:6, fontSize:'0.8rem',
        }}>
          <RefreshCw size={13} style={{ animation: loading ? 'spin 0.6s linear infinite' : 'none' }} />
          Actualizar
        </button>
      </div>

      {/* Filter */}
      <div style={{ background:'#0d1b2e', border:'1px solid #1e3a5f', borderRadius:10, padding:'12px 18px', marginBottom:16, display:'flex', gap:12, alignItems:'center' }}>
        <Search size={14} color="#475569" />
        <input value={search} onChange={e => setSearch(e.target.value)}
          placeholder="Buscar por nombre o email..."
          style={{
            flex:1, background:'transparent', border:'none', outline:'none',
            color:'#e2e8f0', fontSize:'0.85rem', fontFamily:'DM Sans, sans-serif',
          }}
        />
        <span style={{ color:'#334155', fontSize:'0.72rem', fontFamily:'JetBrains Mono, monospace' }}>
          {filtrados.length} usuarios
        </span>
      </div>

      {/* Table */}
      <div style={{ background:'#0d1b2e', border:'1px solid #1e3a5f', borderRadius:12, overflow:'hidden' }}>
        {/* Header */}
        <div style={{
          display:'grid', gridTemplateColumns:'1fr 200px 100px 140px 120px',
          gap:16, padding:'10px 20px',
          background:'#0a1628', borderBottom:'1px solid #1e3a5f',
        }}>
          {['Usuario', 'Email', 'Rol', 'Registro', 'Estado / Acción'].map((h, i) => (
            <span key={i} style={{ color:'#334155', fontSize:'0.68rem', fontFamily:'JetBrains Mono, monospace', textTransform:'uppercase', letterSpacing:'0.08em' }}>{h}</span>
          ))}
        </div>

        {loading ? (
          <div style={{ display:'flex', flexDirection:'column' }}>
            {[...Array(6)].map((_, i) => (
              <div key={i} style={{ height:52, borderBottom:'1px solid #1e3a5f', background: i%2===0 ? 'transparent' : '#0a162844', animation:'pulse 1.5s infinite' }} />
            ))}
          </div>
        ) : filtrados.map((u, i) => (
          <div key={u.id} style={{
            display:'grid', gridTemplateColumns:'1fr 200px 100px 140px 120px',
            gap:16, padding:'12px 20px', alignItems:'center',
            borderBottom: i < filtrados.length-1 ? '1px solid #0a1628' : 'none',
            background: i%2===0 ? 'transparent' : '#0a162822',
            transition:'background 0.15s',
          }}
          onMouseEnter={e => e.currentTarget.style.background = '#112240'}
          onMouseLeave={e => e.currentTarget.style.background = i%2===0 ? 'transparent' : '#0a162822'}
          >
            {/* Nombre */}
            <div style={{ display:'flex', alignItems:'center', gap:10 }}>
              <div style={{
                width:32, height:32, borderRadius:'50%', flexShrink:0,
                background: u.estado === 'BLOQUEADA' ? '#1e1e2e' : 'linear-gradient(135deg, #1d4ed8, #0891b2)',
                display:'flex', alignItems:'center', justifyContent:'center',
                fontSize:'0.8rem', fontWeight:700, color: u.estado === 'BLOQUEADA' ? '#334155' : 'white',
              }}>
                {u.nombre?.[0]?.toUpperCase() || 'U'}
              </div>
              <div>
                <div style={{ color: u.estado === 'BLOQUEADA' ? '#475569' : '#e2e8f0', fontSize:'0.85rem', fontWeight:500 }}>{u.nombre}</div>
                <div style={{ color:'#334155', fontSize:'0.68rem', fontFamily:'JetBrains Mono, monospace' }}>{u.id?.slice(0,8)}...</div>
              </div>
            </div>

            <span style={{ color:'#64748b', fontSize:'0.8rem', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{u.email}</span>

            <span style={{
              fontSize:'0.7rem', fontFamily:'JetBrains Mono, monospace',
              padding:'3px 8px', borderRadius:99,
              background: u.rol === 'admin' ? 'rgba(139,92,246,0.1)' : u.rol === 'analista' ? 'rgba(59,130,246,0.1)' : 'rgba(30,58,95,0.5)',
              border: u.rol === 'admin' ? '1px solid rgba(139,92,246,0.3)' : u.rol === 'analista' ? '1px solid rgba(59,130,246,0.3)' : '1px solid #1e3a5f',
              color: u.rol === 'admin' ? '#a78bfa' : u.rol === 'analista' ? '#60a5fa' : '#64748b',
              textTransform:'uppercase',
            }}>
              {u.rol}
            </span>

            <span style={{ color:'#475569', fontSize:'0.78rem' }}>{timeStr(u.fecha_registro)}</span>

            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <span style={{
                fontSize:'0.7rem', fontFamily:'JetBrains Mono, monospace',
                color: u.estado === 'ACTIVA' ? '#10b981' : '#ef4444',
              }}>
                {u.estado === 'ACTIVA' ? '● ACTIVA' : '● BLOQUEADA'}
              </span>
              {u.rol === 'usuario' && (
                <button onClick={() => toggleBloqueo(u)} disabled={!!actionLoading[u.id]} style={{
                  background:'none', border:'1px solid #1e3a5f', borderRadius:6,
                  padding:'4px 8px', cursor:'pointer',
                  color: u.estado === 'BLOQUEADA' ? '#10b981' : '#ef4444',
                  fontSize:'0.65rem', transition:'all 0.15s',
                  display:'flex', alignItems:'center', gap:4,
                }}>
                  {actionLoading[u.id] ? '...' : u.estado === 'BLOQUEADA'
                    ? <><ShieldCheck size={11} /> Activar</>
                    : <><ShieldOff size={11} /> Bloquear</>
                  }
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.6; } }
        input::placeholder { color: #334155; }
      `}</style>
    </div>
  )
}
